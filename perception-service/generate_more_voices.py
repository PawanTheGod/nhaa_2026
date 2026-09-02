"""
Generate More Real Human Spoken Voice Recordings for Comprehensive AI Perception Testing
==============================================================================
Creates 4 new real human voice MP3 audio files across Hindi, Marathi, English, and Tamil:
1. voice_suicidal_hindi.mp3 (Suicidal Ideation & Depression)
2. voice_trauma_marathi.mp3 (Trauma & Physical Abuse)
3. voice_intimidation_english.mp3 (Blackmail & Severe Violence Threat)
4. voice_vulnerability_tamil.mp3 (Extreme Vulnerability & Danger)
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
    print(f"➜ Synthesizing spoken voice ({lang_code}): \"{text}\"...")
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(filename)
    abs_path = os.path.abspath(filename)
    print(f"  [SAVED] {abs_path}")
    return filename


def run_more_voice_tests():
    print("=" * 80)
    print("  GENERATING MORE REAL HUMAN VOICE AUDIO FILES & RUNNING PERCEPTION TESTS")
    print("=" * 80)

    service = PerceptionService()
    service.load_models()

    scenarios = [
        {
            "id": 1,
            "filename": "voice_suicidal_hindi.mp3",
            "lang": "hi",
            "title": "Voice 1: Hindi Suicidal Ideation & Depression Emergency Call",
            "text": "मैं जीना नहीं चाहता, मुझे अपनी जिंदगी खत्म करनी है, कोई मेरी मदद नहीं करता"
        },
        {
            "id": 2,
            "filename": "voice_trauma_marathi.mp3",
            "lang": "mr",
            "title": "Voice 2: Marathi Trauma & Physical Abuse Emergency Call",
            "text": "माझ्यावर खूप अत्याचार झाला आहे, मी खूप धक्क्यात आहे, मला वाचवा"
        },
        {
            "id": 3,
            "filename": "voice_intimidation_english.mp3",
            "lang": "en",
            "title": "Voice 3: English Violence Threat & Blackmail Call",
            "text": "Someone is blackmailing me and threatening to kill my family, I need emergency police help right now!"
        },
        {
            "id": 4,
            "filename": "voice_vulnerability_tamil.mp3",
            "lang": "ta",
            "title": "Voice 4: Tamil Extreme Vulnerability & Panic Call",
            "text": "எனக்கு உதவி வேண்டும், நான் மிகவும் பயந்துபோய் இருக்கிறேன், எனக்கு வேறு வழியில்லை"
        }
    ]

    generated_uris = []

    for sc in scenarios:
        print(f"\n" + "-" * 80)
        print(f"Case {sc['id']}: {sc['title']}")
        print("-" * 80)

        # 1. Synthesize audio file
        mp3_file = create_gtts_file(sc["text"], sc["lang"], sc["filename"])
        file_uri = pathlib.Path(mp3_file).resolve().as_uri()
        generated_uris.append((sc["title"], file_uri, mp3_file))

        with open(mp3_file, "rb") as f:
            audio_bytes = f.read()

        # 2. Process via AI Perception Layer
        t0 = time.time()
        result = service.analyze(
            audio_bytes=audio_bytes,
            filename=mp3_file,
            language=sc["lang"],
            case_id=f"MORE-VOICE-{sc['id']}",
            channel="ivrs"
        )
        latency = (time.time() - t0) * 1000.0

        print(f"\n[AI PERCEPTION LIVE RESULT - {sc['lang'].upper()}]")
        print(f"  • Audio File URI     : {file_uri}")
        print(f"  • STT Transcript     : \"{result.stt_transcript}\"")
        print(f"  • Language Status    : {result.language.name} [{result.language.tested_status}]")
        print(f"  • SVI Score          : {result.svi.score} / 100")
        print(f"  • Risk Tier Assigned : {result.svi.risk_tier}")
        print(f"  • Analysis Latency   : {latency:.1f} ms ({latency/1000.0:.3f}s)")

        print("\n  • Risk Flags & Evidence Signals:")
        for flag in result.flags:
            print(f"    - [{flag.name.upper()}] Confidence: {flag.confidence*100:.1f}% | Modality: {flag.source}")
            for sig in flag.signals:
                print(f"      * {sig}")

    print("\n" + "=" * 80)
    print("  ALL 4 NEW REAL HUMAN VOICE RECORDINGS GENERATED & TESTED!")
    print("  You can play these audio files on your PC or upload them in Swagger UI / Tester Page:")
    for title, uri, filename in generated_uris:
        print(f"  🔊 {title}")
        print(f"     URI: {uri}")
    print("=" * 80)


if __name__ == "__main__":
    run_more_voice_tests()
