"""
Twilio IVRS voice webhook — Multi-language call flow with <Record>.

Call flow when someone dials the Twilio number:
  1. POST /twilio/voice             → Language menu  (1=English, 2=Hindi, 3=Marathi)
  2. POST /twilio/gather-lang       → Role menu      (1=Victim, 2=Informer)
  3. POST /twilio/gather-role       → Plays prompt + <Record>
  4. POST /twilio/recording-complete → Twilio POSTs recording URL here
     → Download audio → Deepgram REST transcribe → orchestrator → case created

Test without Twilio:  POST /calls/transcript  with JSON {"transcript": "..."}
                     POST /calls/test-auto     (pre-baked demo, no setup)
"""
from __future__ import annotations

import os
import json
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
import httpx

from app.services.calls.orchestrator import process_transcript_to_case
from app.services.stt.deepgram_client import transcribe_bytes, DEEPGRAM_API_KEY
from app.database import AsyncSessionLocal
from app.routes.websocket import ws_manager

log = logging.getLogger("nhaa.twilio")

router = APIRouter(tags=["twilio"])


# ─── IVRS text strings for each language ────────────────────────────────────
IVRS = {
    "en": {
        "tts_lang": "en-IN",
        "tts_voice": "Polly.Aditi",
        "dg_lang": "en-IN",
        "role_prompt": (
            "You have selected English. "
            "Press 1 if you are a victim. "
            "Press 2 if you are an informer."
        ),
        "record_prompt": (
            "Please describe your complaint clearly after the tone. "
            "State your full name, location, and what occurred. "
            "When you finish speaking, please press the hash key to hear your official confirmation."
        ),
        "victim_label": "victim",
        "informer_label": "informer",
        "error_msg": "We are sorry, there was an error. Please call again.",
    },
    "hi": {
        "tts_lang": "hi-IN",
        "tts_voice": "Polly.Aditi",
        "dg_lang": "hi",
        "role_prompt": (
            "Aapne Hindi chunaa. "
            "Agar aap peedit hain to 1 dabayen. "
            "Agar aap soochna dene waale hain to 2 dabayen."
        ),
        "record_prompt": (
            "Beep ke baad apni shikayat vistaar se batayein. "
            "Apna naam, sthaan, aur ghatna ki poori jaankari dein. "
            "Bolne ke baad kripya hash ka button dabayein taaki aapko shikayat darj hone ki pushti sunai de."
        ),
        "victim_label": "peedit",
        "informer_label": "soochna_deta",
        "error_msg": "Maafi chahte hain, ek galti hui. Kripya dobara call karein.",
    },
    "mr": {
        "tts_lang": "mr-IN",
        "tts_voice": "Polly.Aditi",
        "dg_lang": "mr",
        "role_prompt": (
            "Tumhi Marathi nivadli. "
            "Tumhi peetit asel tar 1 daba. "
            "Tumhi mahiti denara asel tar 2 daba."
        ),
        "record_prompt": (
            "Beep nantar tumchi takraar vistaarane sangaa. "
            "Tumcha naav, thikaan ani ghatna sangaa. "
            "Zhalyavar krupaya hash button daba jyamule tumhala pushti aiku yeyil."
        ),
        "victim_label": "peetit",
        "informer_label": "mahiti_denara",
        "error_msg": "Maafi aahe, ek chook zhaali. Krupaya parat call kara.",
    },

}

LANG_DIGIT_MAP = {"1": "en", "2": "hi", "3": "mr"}
ROLE_DIGIT_MAP = {"1": "victim", "2": "informer"}


def _twiml(content: str) -> Response:
    return Response(
        content=f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n{content}\n</Response>',
        media_type="application/xml",
    )


def _say(text: str, lang_code: str = "en") -> str:
    cfg = IVRS[lang_code]
    return f'  <Say voice="{cfg["tts_voice"]}" language="{cfg["tts_lang"]}">{text}</Say>'


# ─── Step 1: Language selection ──────────────────────────────────────────────
@router.post("/twilio/voice")
async def twilio_voice(request: Request):
    base = str(request.base_url).rstrip("/")
    action = f"{base}/twilio/gather-lang"

    body = "\n".join([
        f'  <Gather numDigits="1" action="{action}" method="POST" timeout="10">',
        '    <Say voice="Polly.Aditi" language="en-IN">Welcome to the National Helpline Against Atrocities. Press 1 for English.</Say>',
        '    <Say voice="Polly.Aditi" language="hi-IN">Rashtriya Atyachar Virodhi Helpline mein aapka swagat hai. Hindi ke liye 2 dabayen.</Say>',
        '    <Say voice="Polly.Aditi" language="mr-IN">Rashtriya Atyachar Virodhi Helpline madhe swagat aahe. Marathi sathi 3 daba.</Say>',
        '  </Gather>',
        '  <Say voice="Polly.Aditi" language="hi-IN">Koi input nahi mila. Kripya dobara call karein.</Say>',
        '  <Hangup/>',
    ])
    return _twiml(body)


# ─── Step 2: Language received → Role menu ───────────────────────────────────
@router.post("/twilio/gather-lang")
async def twilio_gather_lang(request: Request):
    form = await request.form()
    digit = form.get("Digits", "").strip()
    lang = LANG_DIGIT_MAP.get(digit, "hi")
    cfg = IVRS[lang]

    base = str(request.base_url).rstrip("/")
    action = f"{base}/twilio/gather-role?lang={lang}"

    body = "\n".join([
        f'  <Gather numDigits="1" action="{action}" method="POST" timeout="10">',
        _say(cfg["role_prompt"], lang),
        '  </Gather>',
        _say(cfg["error_msg"], lang),
        '  <Hangup/>',
    ])
    log.info("Language selected: digit=%s lang=%s", digit, lang)
    return _twiml(body)


# ─── Step 3: Role received → Speech complaint (uses Gather input=speech) ─────
# NOTE: We use <Gather input="speech"> instead of <Record> because Twilio
# trial accounts do NOT support <Record>. Gather+speech works on all accounts
# and gives us the transcript directly via SpeechResult — no audio download
# or Deepgram needed.

SPEECH_PROMPTS = {
    "en": (
        "Please describe your complaint clearly now. "
        "State your full name, location, and what occurred. "
        "When you finish speaking, press the hash key or stay silent for a few seconds."
    ),
    "hi": (
        "Kripya apni shikayat ab vistaar se batayein. "
        "Apna naam, sthaan, aur ghatna ki poori jaankari dein. "
        "Bolne ke baad kripya hash ka button dabayein ya kuch der chup rahein."
    ),
    "mr": (
        "Krupaya tumchi takraar aata vistaarane sangaa. "
        "Tumcha naav, thikaan ani ghatna sangaa. "
        "Zhalyavar krupaya hash button daba kinva shant raha."
    ),
}

@router.post("/twilio/gather-role")
async def twilio_gather_role(request: Request):
    form = await request.form()
    digit = form.get("Digits", "").strip()
    lang = request.query_params.get("lang", "hi")
    role_key = ROLE_DIGIT_MAP.get(digit, "victim")
    cfg = IVRS.get(lang, IVRS["hi"])
    role_label = cfg["victim_label"] if role_key == "victim" else cfg["informer_label"]

    base = str(request.base_url).rstrip("/")
    action = f"{base}/twilio/speech-done?lang={lang}&amp;role={role_label}"

    log.info("Role selected: digit=%s role=%s lang=%s", digit, role_label, lang)

    prompt_text = SPEECH_PROMPTS.get(lang, SPEECH_PROMPTS["hi"])
    speech_lang = cfg["tts_lang"]  # e.g. "hi-IN", "en-IN"

    body = "\n".join([
        f'  <Gather input="speech" action="{action}" method="POST" '
        f'language="{speech_lang}" speechTimeout="5" timeout="60" '
        f'finishOnKey="#">',
        _say(prompt_text, lang),
        '  </Gather>',
        _say(cfg["error_msg"], lang),
        '  <Hangup/>',
    ])
    return _twiml(body)


# ─── Step 4: Speech captured → Create case + Speak acknowledgment ────────────
ACK_MESSAGES = {
    "hi": (
        "Dhanyavaad. Aapki shikayat safaltapoorvak darj kar li gayi hai. "
        "Sambandhit jila police DSP adhikari ko jaanch ke liye turant soochit kar diya gaya hai. "
        "Aapki shikayat dashboard par darj ho chuki hai. "
        "Rashtriya Helpline 14566 mein sampark karne ke liye dhanyavaad."
    ),
    "en": (
        "Thank you. Your complaint has been successfully registered. "
        "The District Superintendent of Police has been notified for immediate investigation. "
        "Your complaint has been logged in the official intelligence queue. "
        "Thank you for contacting the National Helpline 14566."
    ),
    "mr": (
        "Dhanyavaad. Tumchi takraar yashasviritya nondavali geli aahe. "
        "Sambandhit jilha DSP adhikaryanna lagech choukashi sathi soochit kele aahe. "
        "Rashtriya Helpline 14566 var sampark kelya baddal dhanyavaad."
    ),
}

@router.api_route("/twilio/speech-done", methods=["GET", "POST"])
async def twilio_speech_done(request: Request):
    """
    Called by Twilio after <Gather input="speech"> completes.
    Twilio sends SpeechResult (the transcript) directly.
    We create the case from the transcript and speak the acknowledgment.
    """
    form = {}
    if request.method == "POST":
        try:
            form = await request.form()
        except Exception:
            pass

    lang = request.query_params.get("lang") or "hi"
    role = request.query_params.get("role") or "victim"
    transcript = form.get("SpeechResult", "")
    caller_phone = form.get("From", "")
    call_sid = form.get("CallSid", "")

    log.info("Speech captured: call=%s from=%s lang=%s role=%s transcript=%s",
             call_sid, caller_phone, lang, role, transcript[:200] if transcript else "(empty)")

    # Process the transcript into a case (non-blocking — even if it fails, still acknowledge)
    if transcript and transcript.strip():
        try:
            result = await process_transcript_to_case(
                transcript,
                channel="voice_twilio",
                caller_phone=caller_phone or None,
                db_session_factory=AsyncSessionLocal,
                broadcast_websocket=ws_manager.broadcast,
                extra_meta={"language": lang, "caller_role": role},
            )
            log.info("Case created from speech: case_id=%s tier=%s", result.get("case_id"), result.get("risk_tier"))
        except Exception as e:
            log.exception("Failed to create case from speech: %s", e)
    else:
        log.warning("Empty SpeechResult from call %s", call_sid)

    # Always play the spoken acknowledgment
    msg = ACK_MESSAGES.get(lang, ACK_MESSAGES["hi"])
    body = "\n".join([
        _say(msg, lang),
        '  <Pause length="2"/>',
        '  <Hangup/>',
    ])
    return _twiml(body)


# ─── Legacy record-done (kept for backward compatibility) ────────────────────
@router.api_route("/twilio/record-done", methods=["GET", "POST"])
async def twilio_record_done(request: Request):
    lang = request.query_params.get("lang") or "hi"
    msg = ACK_MESSAGES.get(lang, ACK_MESSAGES["hi"])
    body = "\n".join([
        _say(msg, lang),
        '  <Pause length="2"/>',
        '  <Hangup/>',
    ])
    return _twiml(body)



# ─── Step 4: Recording complete → Download + Transcribe + Create Case ────────
@router.post("/twilio/recording-complete")
async def twilio_recording_complete(request: Request):
    """
    Twilio POSTs here when recording is ready.
    Form fields include: RecordingUrl, RecordingSid, RecordingDuration, CallSid, From, To.
    """
    form = await request.form()
    recording_url = form.get("RecordingUrl", "")
    recording_sid = form.get("RecordingSid", "")
    call_sid = form.get("CallSid", "")
    caller_phone = form.get("From", "")
    duration = form.get("RecordingDuration", "0")
    lang = request.query_params.get("lang", "hi")
    role = request.query_params.get("role", "victim")

    log.info(
        "Recording complete: sid=%s call=%s from=%s duration=%ss lang=%s role=%s url=%s",
        recording_sid, call_sid, caller_phone, duration, lang, role, recording_url,
    )

    if not recording_url:
        log.warning("No RecordingUrl in callback")
        return {"status": "error", "detail": "no recording url"}

    # Twilio recording URL needs .wav appended to get raw audio
    audio_url = f"{recording_url}.wav"

    # Download the recording (Twilio requires Basic auth for trial accounts)
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if account_sid and auth_token:
                r = await client.get(audio_url, auth=(account_sid, auth_token))
            else:
                r = await client.get(audio_url)
            r.raise_for_status()
            audio_bytes = r.content
    except Exception as e:
        log.exception("Failed to download recording: %s", e)
        return {"status": "error", "detail": f"download failed: {e}"}

    log.info("Downloaded recording: %d bytes", len(audio_bytes))

    # Transcribe via Deepgram REST API
    dg_lang = IVRS.get(lang, IVRS["hi"])["dg_lang"]
    try:
        transcript = await transcribe_bytes(audio_bytes, language=dg_lang, mimetype="audio/wav")
    except Exception as e:
        log.exception("Deepgram transcription failed: %s", e)
        return {"status": "error", "detail": f"transcription failed: {e}"}

    if not transcript.strip():
        log.warning("Empty transcript from recording %s", recording_sid)
        return {"status": "ignored", "reason": "empty transcript"}

    log.info("Transcript (lang=%s, %d chars): %s", lang, len(transcript), transcript[:200])

    # Run through the full pipeline
    try:
        result = await process_transcript_to_case(
            transcript,
            channel="voice_twilio",
            caller_phone=caller_phone or None,
            db_session_factory=AsyncSessionLocal,
            broadcast_websocket=ws_manager.broadcast,
            extra_meta={"language": lang, "caller_role": role},
        )
        log.info("Case created from recording: case_id=%s tier=%s", result.get("case_id"), result.get("risk_tier"))
        return {"status": "ok", **result}
    except Exception as e:
        log.exception("Orchestrator failed: %s", e)
        return {"status": "error", "detail": f"orchestrator failed: {e}"}


# ─── Test endpoint: submit a transcript without Twilio ───────────────────────
class TranscriptPayload(BaseModel):
    transcript: str
    channel: Optional[str] = "voice_twilio"
    caller_phone: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    language: Optional[str] = "hi"
    caller_role: Optional[str] = "victim"


@router.post("/calls/transcript")
async def calls_transcript(payload: TranscriptPayload):
    if not payload.transcript.strip():
        raise HTTPException(status_code=400, detail="transcript is empty")
    result = await process_transcript_to_case(
        payload.transcript,
        channel=payload.channel or "voice_twilio",
        caller_phone=payload.caller_phone,
        district=payload.district,
        state=payload.state,
        db_session_factory=AsyncSessionLocal,
        broadcast_websocket=ws_manager.broadcast,
        extra_meta={"language": payload.language, "caller_role": payload.caller_role},
    )
    return JSONResponse(result)


@router.post("/calls/transcribe")
async def calls_transcribe(request: Request, language: str = "hi"):
    if not DEEPGRAM_API_KEY:
        raise HTTPException(status_code=503, detail="DEEPGRAM_API_KEY not configured")
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="empty audio body")
    content_type = request.headers.get("content-type", "audio/wav")
    try:
        transcript = await transcribe_bytes(body, language=language, mimetype=content_type)
    except Exception as e:
        log.exception("transcribe failed: %s", e)
        raise HTTPException(status_code=502, detail=f"Deepgram error: {e}")
    return {"transcript": transcript, "language": language, "bytes": len(body)}


@router.get("/calls/health")
async def calls_health():
    return {
        "twilio_configured": bool(os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN")),
        "deepgram_configured": bool(DEEPGRAM_API_KEY),
        "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
        "twilio_number": os.getenv("TWILIO_PHONE_NUMBER", ""),
        "ivrs_languages": ["en", "hi", "mr"],
    }


# ─── Retell webhook ──────────────────────────────────────────────────────────
class RetellCallEnded(BaseModel):
    event: Optional[str] = "call_ended"
    call: Optional[dict] = None

@router.post("/calls/retell-webhook")
async def retell_webhook(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON")
    call = body.get("call") or body
    transcript = call.get("transcript") or call.get("transcript_text") or ""
    caller = call.get("from_number") or call.get("customer_number")
    if not transcript.strip():
        return {"status": "ignored", "reason": "empty transcript"}
    result = await process_transcript_to_case(
        transcript, channel="voice_retell", caller_phone=caller,
        db_session_factory=AsyncSessionLocal, broadcast_websocket=ws_manager.broadcast,
    )
    return {"status": "ok", **result}


# ─── Automated test ──────────────────────────────────────────────────────────
@router.post("/calls/test-auto")
async def test_auto():
    samples = [
        {
            "label": "Critical (Hindi) - assault + police refused FIR",
            "transcript": "Mere gaon mein ek Dalit parivar par hamla hua hai. Paanch logon ne lathiyon aur iron rods se maara. Police station gaya par unhone FIR register nahi ki.",
            "channel": "voice_twilio", "caller_phone": "+91-98765-43210",
            "district": "Central Delhi", "state": "Delhi",
            "language": "hi", "caller_role": "peedit",
        },
        {
            "label": "Moderate (English) - social boycott",
            "transcript": "Our village is boycotting us because we are Dalit. They are not letting us draw water from the well and the landlord has not paid our wages for 3 months.",
            "channel": "voice_twilio", "caller_phone": "+1-415-555-0199",
            "district": "Ranchi", "state": "Jharkhand",
            "language": "en", "caller_role": "victim",
        },
        {
            "label": "Urgent (Marathi) - land grab",
            "transcript": "Amchya jamin var jabordasti kabja kela ahe. Sahukarane amhala ghar sodnyacha dhakka dila. Police madhe takraar divali pan kahi kela nahi.",
            "channel": "voice_twilio", "caller_phone": "+91-77890-12345",
            "district": "Pune", "state": "Maharashtra",
            "language": "mr", "caller_role": "peetit",
        },
    ]
    results = []
    for s in samples:
        r = await process_transcript_to_case(
            s["transcript"], channel=s["channel"], caller_phone=s["caller_phone"],
            district=s["district"], state=s["state"],
            db_session_factory=AsyncSessionLocal, broadcast_websocket=ws_manager.broadcast,
            extra_meta={"language": s["language"], "caller_role": s["caller_role"]},
        )
        r["label"] = s["label"]
        results.append(r)
    return {"test_run": True, "results": results}
