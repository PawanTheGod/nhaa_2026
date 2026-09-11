"""
app/services/agent/groq_extractor.py
────────────────────────────────────
Ultra-low-latency entity and intelligence extraction using Groq Cloud API.
Extracts victim name, incident location, assault date, case summary, and risk flags
from multilingual IVRS / telephony voice transcripts (Hindi, Marathi, English, etc.).
"""

import os
import re
import json
import logging
from typing import Optional, Any
from pathlib import Path
from dotenv import load_dotenv
import httpx

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

log = logging.getLogger("nhaa.groq_extractor")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

EXTRACTION_SYSTEM_PROMPT = """You are the AI Perception & Forensic Entity Extraction engine for the National Helpline Against Atrocities (14566), Ministry of Social Justice & Empowerment, Government of India.

Analyze the given voice call transcript (which may be in Hindi, Marathi, English, Tamil, etc.) and extract structured case examination fields.

Return ONLY a JSON object with this EXACT schema:
{
  "person_name": "<Full name of the victim or complainant if mentioned, or null>",
  "incident_location": "<Specific village, ward, district, landmark or address mentioned, or null>",
  "person_assaulted_date_str": "<Mentioned date/time of incident e.g. 'Yesterday at 9 PM', '2 days ago', or null>",
  "case_summary": "<Comprehensive 2-4 sentence factual English summary of the grievance, accused, and harm>",
  "recommended_action": "<One of: 'police_intervention', 'legal_aid', 'medical_assistance', 'counselling', 'emergency_escalation', 'fir_registration'>",
  "flags": [
    {
      "name": "<One of: 'physical_violence', 'verbal_threat', 'social_exclusion', 'police_complicity', 'gender_violence', 'child_violence', 'trauma', 'property_damage', 'documentation', 'economic_exploitation'>",
      "confidence": <float 0.0 to 1.0>,
      "signals": ["<exact words from transcript>"]
    }
  ]
}

Rules:
1. Extract Indian names accurately (e.g., 'Ramesh Kumar', 'Sunita Devi', 'Vikram Singh'). If not explicitly stated, return null.
2. Extract exact locations (e.g., 'Gram Kalyanpur, District Gaya', 'Ward No. 4, Central Delhi').
3. Support Hindi, Hinglish, Marathi, Tamil, Bengali, English transliterated text.
4. Output valid JSON only without markdown fences or extra explanations.
"""


async def extract_case_entities_with_groq(transcript: str, language: str = "en") -> dict[str, Any]:
    """
    Calls Groq API to extract person_name, location, summary, and flags with sub-second response time.
    """
    if not GROQ_API_KEY:
        log.warning("GROQ_API_KEY is not configured")
        return {}

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT.strip()},
            {"role": "user", "content": f"Language: {language}\n\nCall Transcript:\n\"\"\"{transcript[:3500]}\"\"\""},
        ],
        "temperature": 0.1,
        "max_tokens": 800,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(GROQ_API_URL, headers=headers, json=payload)
            if resp.status_code != 200:
                log.error("Groq API error (%s): %s", resp.status_code, resp.text)
                return {}

            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            # Clean markdown codeblocks if present
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.MULTILINE).strip()
            result = json.loads(content)
            log.info("Groq extraction successful for transcript (%d chars) -> person_name: %s, location: %s",
                     len(transcript), result.get("person_name"), result.get("incident_location"))
            return result
    except Exception as e:
        log.error("Groq entity extraction failed: %s", e)
        return {}
