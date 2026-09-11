"""
app/services/tts/sarvam_tts.py
──────────────────────────────
High-fidelity Indian Voice Text-to-Speech (TTS) using Sarvam AI's bulbul:v3 model.
Generates authentic Indian accents (Hindi, Marathi, Indian English, Tamil, Telugu, etc.)
with local audio caching for zero-latency IVRS playback.
"""

import os
import hashlib
import base64
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import httpx

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

log = logging.getLogger("nhaa.sarvam_tts")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
TTS_CACHE_DIR = Path("uploads/tts_cache")

# Speaker voice mappings for natural Indian accents
DEFAULT_SPEAKERS = {
    "hi": "priya",       # Authentic Hindi female tone
    "hi-IN": "priya",
    "mr": "rupali",      # Authentic Marathi speaker
    "mr-IN": "rupali",
    "en": "simran",      # Natural Indian English
    "en-IN": "simran",
    "ta": "gokul",       # Tamil speaker
    "ta-IN": "gokul",
    "te": "kavitha",     # Telugu speaker
    "te-IN": "kavitha",
    "bn": "roopa",       # Bengali speaker
    "bn-IN": "roopa",
}

LANGUAGE_CODE_MAP = {
    "hi": "hi-IN",
    "mr": "mr-IN",
    "en": "en-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "bn": "bn-IN",
}


def _get_cache_filename(text: str, lang_code: str, speaker: str) -> Path:
    TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    h = hashlib.md5(f"{lang_code}:{speaker}:{text}".encode("utf-8")).hexdigest()
    return TTS_CACHE_DIR / f"{h}.wav"


async def generate_sarvam_speech(
    text: str,
    language: str = "hi",
    speaker: Optional[str] = None,
    pitch: float = 0.0,
    pace: float = 1.0,
) -> Optional[bytes]:
    """
    Generates WAV audio bytes using Sarvam AI's bulbul:v3 TTS model.
    Checks local disk cache first for sub-millisecond retrieval.
    """
    if not text or not text.strip():
        return None

    lang_key = language.lower().replace("-in", "")
    target_lang = LANGUAGE_CODE_MAP.get(lang_key, "hi-IN")
    chosen_speaker = speaker or DEFAULT_SPEAKERS.get(target_lang, "priya")

    cache_file = _get_cache_filename(text, target_lang, chosen_speaker)
    if cache_file.exists():
        try:
            return cache_file.read_bytes()
        except Exception:
            pass

    if not SARVAM_API_KEY:
        log.warning("SARVAM_API_KEY is not configured")
        return None

    payload = {
        "inputs": [text.strip()],
        "target_language_code": target_lang,
        "speaker": chosen_speaker,
        "pitch": pitch,
        "pace": pace,
        "loudness": 1.5,
        "speech_sample_rate": 8000,  # 8kHz telephony standard for Twilio/IVRS
        "enable_preprocessing": True,
        "model": "bulbul:v3",
    }

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(SARVAM_TTS_URL, json=payload, headers=headers)
            if resp.status_code != 200:
                log.error("Sarvam TTS API Error (%s): %s", resp.status_code, resp.text)
                return None

            data = resp.json()
            audios = data.get("audios", [])
            if not audios:
                log.error("Sarvam TTS returned empty audios array")
                return None

            audio_bytes = base64.b64decode(audios[0])
            cache_file.write_bytes(audio_bytes)
            log.info("Generated Sarvam TTS audio: %d bytes (lang=%s, speaker=%s)", len(audio_bytes), target_lang, chosen_speaker)
            return audio_bytes
    except Exception as e:
        log.error("Sarvam TTS generation failed: %s", e)
        return None
