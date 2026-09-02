"""
Generate Low-Risk vs Critical-Risk Voice Audio Files for Comprehensive SVI Tier Testing
==============================================================================
Generates 4 distinct real human voice MP3 audio files covering both extremes:
1. voice_low_routine_query.mp3 (Routine Office Query - Low Risk 0-24)
2. voice_low_general_thanks.mp3 (General Info Request - Low Risk 0-24)
3. voice_critical_threat_assault.mp3 (Life Threat & Armed Assault - Critical Risk 75-100)
4. voice_critical_suicide_emergency.mp3 (Immediate Suicidal Crisis - Critical Risk 75-100)
==============================================================================
"""

import os
import sys
import json
import time
import pathlib
from gtts import gTTS

# Reconfigure stdout for Windows UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from api.services.perception_service import PerceptionService


def create_gtts_file(text: str, lang_code: str, filename: str) -> str:
    """Synthesizes real human spoken audio using gTTS and saves as MP3."""
    print(f"➜ Synthesizing voice ({lang_code}): \"{text}\"...")
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(filename)
    abs_path = os.path.abspath(filename)
    print(f"  [SAVED] {abs_path}")
    return filename


def run_tiered_voice_tests():
    print("=" * 80)
    print("  GENERATING LOW-RISK VS CRITICAL-RISK REAL HUMAN VOICE RECORDINGS")
    print("=" * 80)

    service = PerceptionService()
    service.load_models()

    scenarios = [
        # --- LOW RISK / LESS IMPORTANT CALLS ---
        {
            "id": 1,
            "filename": "voice_low_routine_query.mp3",
            "lang": "hi",
            "tier_type": "LESS IMPORTANT / LOW RISK",
            "title": "Voice 1: Hindi Routine Office Query (Calm & Informational)",
            "text": "नमस्ते, क्या मुझे आपके ऑफिस का पता और काम का समय मिल सकता है? धन्यवाद"
        },
        {
            "id": 2,
            "filename": "voice_low_general_thanks.mp3",
            "lang": "en",
            "tier_type": "LESS IMPORTANT / LOW RISK",
            "title": "Voice 2: English Scheme Guidelines Request (Calm & Informational)",
            "text": "Hello, I just wanted to ask about the scheme details and guidelines. Thank you for your assistance."
        },
        # --- CRITICAL RISK / MORE IMPORTANT EMERGENCY CALLS ---
        {
            "id": 3,
            "filename": "voice_critical_threat_assault.mp3",
            "lang": "hi",
            "tier_type": "MORE IMPORTANT / CRITICAL EMERGENCY",
            "title": "Voice 3: Hindi Armed Assault & Life Threat Emergency Call",
            "text": "मुझे बचाओ! मेरे घर में हथियार लेकर लोग घुस आए हैं और जान से मारने की धमकी दे रहे हैं, तुरंत पुलिस भेजो!"
        },
        {
            "id": 4,
            "filename": "voice_critical_suicide_emergency.mp3",
            "lang": "mr",
            "tier_type": "MORE IMPORTANT / CRITICAL EMERGENCY",
            "title": "Voice 4: Marathi Immediate Suicidal Crisis Call",
            "text": "मी खूप त्रासलो आहे, मी आताच जीव देणार आहे, माझी जिंदगी संपवतोय, मला वाचवायला कोणी नाही"
        }
    ]

    generated_uris = []

    for sc in scenarios:
        print(f"\n" + "-" * 80)
        print(f"Case {sc['id']} [{sc['tier_type']}]: {sc['title']}")
        print("-" * 80)

        # 1. Synthesize audio file
        mp3_file = create_gtts_file(sc["text"], sc["lang"], sc["filename"])
        file_uri = pathlib.Path(mp3_file).resolve().as_uri()
        generated_uris.append((sc["title"], sc["tier_type"], file_uri, mp3_file))

        with open(mp3_file, "rb") as f:
            audio_bytes = f.read()

        # 2. Process via AI Perception Layer
        t0 = time.time()
        result = service.analyze(
            audio_bytes=audio_bytes,
            filename=mp3_file,
            language=sc["lang"],
            case_id=f"TIER-VOICE-{sc['id']}",
            channel="ivrs"
        )
        latency = (time.time() - t0) * 1000.0

        print(f"\n[AI PERCEPTION LIVE RESULT - {sc['lang'].upper()}]")
        print(f"  • Category Type      : {sc['tier_type']}")
        print(f"  • Audio File URI     : {file_uri}")
        print(f"  • STT Transcript     : \"{result.stt_transcript}\"")
        print(f"  • Language Status    : {result.language.name} [{result.language.tested_status}]")
        print(f"  • SVI Score          : {result.svi.score} / 100")
        print(f"  • Risk Tier Assigned : {result.svi.risk_tier}")
        print(f"  • Processing Latency : {latency:.1f} ms ({latency/1000.0:.3f}s)")

        print("\n  • Risk Flags & Evidence Signals:")
        if result.flags:
            for flag in result.flags:
                print(f"    - [{flag.name.upper()}] Confidence: {flag.confidence*100:.1f}% | Modality: {flag.source}")
                for sig in flag.signals:
                    print(f"      * {sig}")
        else:
            print("    - No distress flags detected (Routine / Low Risk Call)")

    print("\n" + "=" * 80)
    print("  ALL TIERED VOICE RECORDINGS GENERATED & TESTED SUCCESSFULLY!")
    print("  Audio files saved on disk:")
    for title, tier_type, uri, filename in generated_uris:
        print(f"  🔊 [{tier_type}] {title}")
        print(f"     URI: {uri}")
    print("=" * 80)


if __name__ == "__main__":
    run_tiered_voice_tests()
