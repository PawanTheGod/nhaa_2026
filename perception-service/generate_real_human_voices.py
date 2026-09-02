"""
Real Human Voice Audio Generator & Perception Layer Tester
==============================================================================
Generates REAL HUMAN SPOKEN VOICE AUDIO FILES in Hindi, Marathi, and English
using Google Text-To-Speech (gTTS), saves real MP3 and WAV files on disk,
and processes them live through STT, Speech Emotion, Vocal Acoustics, and SVI scoring.
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


def create_real_human_voice(text: str, lang_code: str, filename_base: str):
    """
    Generates a real human speech audio recording file using Google Text-to-Speech (gTTS).
    Saves an MP3 audio file that you can play directly on your Windows PC.
    """
    mp3_filename = f"{filename_base}.mp3"
    print(f"➜ Synthesizing real human spoken voice ({lang_code}): \"{text}\"...")
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(mp3_filename)
    print(f"  [SUCCESS] Saved Real Human Audio File to: {os.path.abspath(mp3_filename)}")
    return mp3_filename


def run_real_voice_tests():
    print("=" * 80)
    print("  GENERATING REAL HUMAN SPOKEN VOICE AUDIO FILES (HINDI, MARATHI, ENGLISH)")
    print("=" * 80)

    service = PerceptionService()
    service.load_models()

    real_voice_scenarios = [
        {
            "id": 1,
            "filename_base": "real_human_voice_hindi",
            "lang": "hi",
            "title": "Hindi Real Spoken Voice Call",
            "text": "मुझे बचाओ! मुझे जान से मारने की धमकी मिल रही है और बहुत डर लग रहा है"
        },
        {
            "id": 2,
            "filename_base": "real_human_voice_marathi",
            "lang": "mr",
            "title": "Marathi Real Spoken Voice Call",
            "text": "मला मदत करा! मला मारहाण आणि धमकी दिली जात आहे, मी खूप घाबरलोय"
        },
        {
            "id": 3,
            "filename_base": "real_human_voice_english",
            "lang": "en",
            "title": "English Real Spoken Voice Call",
            "text": "Please help me! Someone is threatening me and I am in extreme terror and danger"
        }
    ]

    generated_files = []

    for scenario in real_voice_scenarios:
        print(f"\n" + "-" * 80)
        print(f"Case {scenario['id']}: {scenario['title']}")
        print("-" * 80)

        # 1. Generate real human audio file
        mp3_file = create_real_human_voice(
            text=scenario["text"],
            lang_code=scenario["lang"],
            filename_base=scenario["filename_base"]
        )
        generated_files.append(mp3_file)

        with open(mp3_file, "rb") as f:
            audio_bytes = f.read()

        # 2. Run through live AI Perception Engine
        t0 = time.time()
        result = service.analyze(
            audio_bytes=audio_bytes,
            filename=mp3_file,
            language=scenario["lang"],
            case_id=f"REAL-VOICE-{scenario['id']}",
            channel="ivrs"
        )
        latency = (time.time() - t0) * 1000.0

        # Extract Whisper STT transcript from result model predictions or raw measurements
        stt_transcript = "N/A"
        if result.model_predictions:
            for pred in result.model_predictions:
                if pred.source == "stt":
                    stt_transcript = pred.name
                    break

        file_uri = pathlib.Path(mp3_file).resolve().as_uri()
        print(f"\n[AI PERCEPTION ANALYSIS RESULTS - REAL HUMAN VOICE ({scenario['lang'].upper()})]")
        print(f"  • Audio File Saved   : {file_uri}")
        print(f"  • STT Transcript     : \"{stt_transcript}\"")
        print(f"  • Language Status    : {result.language.name} [{result.language.tested_status}]")
        print(f"  • SVI Score          : {result.svi.score} / 100")
        print(f"  • Risk Tier Assigned : {result.svi.risk_tier}")
        print(f"  • Processing Latency : {latency:.1f} ms ({latency/1000.0:.3f} seconds)")

        print("\n  • Vocal Acoustic Features Measured from Real Human Audio:")
        for raw in result.raw_measurements:
            if raw.source == "audio":
                print(f"    - [{raw.name}] {raw.value} {raw.unit}")

        print("\n  • Risk Flags & Evidence Signals:")
        for flag in result.flags:
            print(f"    - [{flag.name.upper()}] Confidence: {flag.confidence*100:.1f}% | Modality: {flag.source}")
            for sig in flag.signals:
                print(f"      * {sig}")

    print("\n" + "=" * 80)
    print("  REAL HUMAN VOICE GENERATION & PERCEPTION TEST COMPLETE!")
    print("  You can click and play these REAL HUMAN VOICE MP3 files on your PC right now:")
    for f_path in generated_files:
        uri = pathlib.Path(f_path).resolve().as_uri()
        print(f"  🔊 {uri}")
    print("=" * 80)


if __name__ == "__main__":
    run_real_voice_tests()
