"""
Call orchestrator: text transcript -> risk flags -> tier -> auto-create case -> broadcast.

Used by:
  - Twilio webhook (real phone call)
  - Browser mic demo (web demo, no Twilio)
  - /api/calls/transcript endpoint (manual / IVRS test)

Pipeline:
  1. OpenRouter LLM extracts {flag_name, confidence, signals[]} from raw Hindi/English/etc text
  2. Aatmman's decision_engine.determine_risk_tier() returns the tier
  3. POST /api/cases (via create_case_service) saves the case to Supabase
  4. POST /api/risk-assessments saves the AI assessment
  5. Broadcast over WebSocket so the operator dashboard updates in real time
  6. Return the case id + tier for TTS playback
"""
from __future__ import annotations

import os
import re
import json
import logging
import asyncio
from typing import Optional

import httpx

from app.services.agent.decision_engine import determine_risk_tier
from app.services.agent.openrouter import OPENROUTER_API_KEY, OPENROUTER_URL, DEFAULT_MODEL

log = logging.getLogger("nhaa.calls")

# OpenRouter LLM call: extract risk flags from free-form text (Hindi, English, Tamil, etc.)
EXTRACT_FLAGS_PROMPT = """You are the perception layer of a government helpline AI. Extract risk signals from a victim's complaint.

Output ONLY a JSON array. No prose. No markdown. No ``` fences.

Schema (one object per signal):
{"name": "<flag>", "confidence": <0..1>, "signals": ["<phrase>"]}

Flag names (use ONLY these exact strings):
- "physical_violence" - assault, beating, injury, blood
- "verbal_threat" - threats, intimidation
- "social_exclusion" - untouchability, boycott, refusal of service
- "police_complicity" - police refused, no FIR, collusion
- "gender_violence" - sexual assault, harassment, dowry
- "child_violence" - victim is a child
- "trauma" - distress, fear, suicidal ideation, silence
- "property_damage" - house/property destroyed
- "documentation" - caste certificate, official documents withheld
- "economic_exploitation" - wages withheld, bonded labor

Rules:
- confidence in [0,1] reflecting how strong the evidence is
- signals[] = exact phrases from the complaint that triggered the flag
- output [] if complaint is benign
- support Hindi, Tamil, Telugu, Bengali, Marathi, English
"""


async def extract_flags_with_llm(transcript: str) -> list[dict]:
    """Call OpenRouter to extract structured risk flags from a free-form transcript."""
    if not OPENROUTER_API_KEY:
        log.warning("OPENROUTER_API_KEY missing - returning empty flags")
        return []

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": EXTRACT_FLAGS_PROMPT.strip()},
            {"role": "user", "content": transcript[:2000]},
        ],
        "temperature": 0.0,
        "max_tokens": 500,
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            content = data["choices"][0]["message"]["content"].strip()
            # Strip markdown fences if any
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.MULTILINE).strip()
            flags = json.loads(content)
            if not isinstance(flags, list):
                log.warning("LLM returned non-list: %s", type(flags))
                return []
            # Validate each flag
            valid = []
            for f in flags:
                if not isinstance(f, dict) or "name" not in f:
                    continue
                f.setdefault("confidence", 0.5)
                f.setdefault("signals", [])
                f["confidence"] = max(0.0, min(1.0, float(f["confidence"])))
                valid.append(f)
            return valid
    except (httpx.HTTPError, json.JSONDecodeError, KeyError, IndexError) as e:
        log.error("OpenRouter extract_flags failed: %s", e)
        return []


# ─── Fallback keyword extractor (no LLM required) ───────────────────────────
KEYWORD_FLAGS = {
    "physical_violence": ["mar", "peet", "attack", "maar", "maara", "assault", "beat", "hit", "blood", "khoon", "injury", "chot"],
    "verbal_threat": ["dhamki", "threat", "dhamka", "warned", "intimidate", "dara", "scared", "डरा"],
    "social_exclusion": ["untouchable", "chheda", "chhut", "boycott", "boycott", "refuse", "gahre pani", "mandir", "temple"],
    "police_complicity": ["police ne", "FIR nahi", "FIR nahi li", "thana", "police refused", "police collusion", "didn't file"],
    "gender_violence": ["rape", "molest", "harass", "dowry", "dahej", "acid", "eve teasing", "stalk"],
    "child_violence": ["bachcha", "bachchi", "child", "minor", "10 saal", "12 saal", "kid"],
    "trauma": ["suicide", "aatmhatya", "depressed", "udaas", "scared", "khauf", "cry", "ro", "hopeless", "give up", "mar jana"],
    "property_damage": ["ghar jalaya", "house burned", "tod", "phenk", "toota", "kuchla"],
    "documentation": ["certificate", "praman", "caste cert", "janata", "document"],
    "economic_exploitation": ["wage", "tankhwah", "kaam nahi", "labour", "paisa nahi"],
}


def extract_flags_keyword(transcript: str) -> list[dict]:
    """Simple keyword-based fallback (works without LLM key, supports English + transliterated Hindi)."""
    text = transcript.lower()
    found = []
    for flag, keywords in KEYWORD_FLAGS.items():
        matched = [kw for kw in keywords if kw.lower() in text]
        if matched:
            conf = min(0.9, 0.5 + 0.1 * len(matched))
            found.append({"name": flag, "confidence": conf, "signals": matched})
    return found


# ─── SVI score estimator (heuristic) ─────────────────────────────────────────
def estimate_svi(transcript: str, flags: list[dict]) -> float:
    """Estimate a 0-99.99 SVI score from transcript length + flag count + confidence.
    Cap at 99.99 to fit NUMERIC(4,2) column on Cases.svi_score / RiskAssessments.svi_score.
    """
    if not flags:
        return 25.0
    base = 30 + 8 * len(flags)
    confidence_bonus = sum(min(0.3, f.get("confidence", 0.5) * 0.3) for f in flags) * 100
    length_bonus = min(20, len(transcript) / 50)
    return min(99.99, base + confidence_bonus + length_bonus)


# ─── Channel inference ───────────────────────────────────────────────────────
def infer_channel(channel: str) -> str:
    """Map incoming channel string to enum value."""
    ch = channel.lower()
    if "voice" in ch or "twilio" in ch or "phone" in ch or "call" in ch:
        return "ivrs"
    if "chatbot" in ch:
        return "chatbot"
    if "mobile" in ch:
        return "mobile_app"
    return "portal"


# ─── Main orchestrator entry point ───────────────────────────────────────────
async def process_transcript_to_case(
    transcript: str,
    *,
    channel: str = "voice_twilio",
    caller_phone: Optional[str] = None,
    district: Optional[str] = None,
    state: Optional[str] = None,
    db_session_factory=None,
    broadcast_websocket=None,
    extra_meta: Optional[dict] = None,
) -> dict:
    """
    Full pipeline: transcript -> flags -> tier -> case -> broadcast.

    Returns: {case_id, risk_tier, flags, svi_score, transcript, channel, status}
    """
    log.info("process_transcript_to_case: %d chars, channel=%s", len(transcript), channel)

    # 1. Extract flags (LLM, fallback to keywords)
    flags = await extract_flags_with_llm(transcript)
    if not flags:
        log.info("LLM returned no flags, trying keyword fallback")
        flags = extract_flags_keyword(transcript)

    # 2. Estimate SVI + determine tier via Aatmman's engine
    svi = estimate_svi(transcript, flags)
    tier = determine_risk_tier(svi, flags)
    tier_value = tier.value if hasattr(tier, "value") else str(tier)

    # 3. Persist to DB
    case_id = None
    ra_id = None
    if db_session_factory is not None:
        try:
            from app.models import Cases, RiskAssessments, RiskTier, CaseStatus, ChannelOrigin
            from datetime import datetime, timezone

            ch_str = infer_channel(channel)
            ch_enum = ChannelOrigin(ch_str) if ch_str in [c.value for c in ChannelOrigin] else ChannelOrigin.ivrs

            meta = extra_meta or {}
            case_language = meta.get("language", "hi")  # from IVRS language selection
            caller_role = meta.get("caller_role", "unknown")

            async with db_session_factory() as db:
                case = Cases(
                    channel_of_origin=ch_enum,
                    district=district or "Central Delhi",
                    state=state or "Delhi",
                    incident_description=transcript[:1000],
                    language=case_language,
                    status=CaseStatus.new,
                    current_level=0,
                    svi_score=svi,
                    risk_tier=RiskTier(tier_value),
                )
                db.add(case)
                await db.flush()
                case_id = case.id

                ra = RiskAssessments(
                    case_id=case_id,
                    svi_score=svi,
                    risk_tier=RiskTier(tier_value),
                    flags={
                        "_extracted": flags,
                        "_source": "voice_intake",
                        "_language": case_language,
                        "_caller_role": caller_role,
                    },
                    explanation_text=(
                        f"[Voice intake | lang={case_language} | role={caller_role}] "
                        f"{len(flags)} flags extracted from {len(transcript)}-char transcript."
                    ),
                    model_version="voice-intake-v1",
                )
                db.add(ra)
                await db.commit()
                log.info(
                    "Created case #%s with tier=%s svi=%.1f flags=%d lang=%s role=%s",
                    case_id, tier_value, svi, len(flags), case_language, caller_role,
                )
        except Exception as e:
            log.exception("DB write failed: %s", e)
            case_id = None

    # 4. Broadcast via WebSocket
    if broadcast_websocket is not None and case_id is not None:
        try:
            msg = {
                "event": "case_created",
                "data": {
                    "id": case_id,
                    "channel_of_origin": infer_channel(channel),
                    "district": district,
                    "state": state,
                    "status": "new",
                    "current_level": 0,
                    "svi_score": svi,
                    "risk_tier": tier_value,
                    "incident_description": transcript[:200],
                    "is_silent_signal": any(f.get("name") == "trauma" for f in flags),
                },
            }
            await broadcast_websocket(msg)
        except Exception as e:
            log.warning("WebSocket broadcast failed: %s", e)

    return {
        "case_id": case_id,
        "risk_tier": tier_value,
        "svi_score": svi,
        "flags": flags,
        "transcript": transcript,
        "channel": channel,
        "caller_phone": caller_phone,
        "status": "created" if case_id else "extracted_only",
    }
