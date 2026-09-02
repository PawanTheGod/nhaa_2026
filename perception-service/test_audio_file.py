"""
Test Your Own Recorded Voice Audio File
==============================================================================
Usage:
    python test_audio_file.py "path/to/your_voice.wav" [language]
==============================================================================
"""

import sys
import os
import json

# Reconfigure stdout for Windows UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from api.services.perception_service import PerceptionService


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_audio_file.py \"path/to/your_recording.wav\" [language_code]")
        print("Example: python test_audio_file.py \"my_voice.mp3\" hi")
        sys.exit(1)

    audio_file_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "hi"

    if not os.path.exists(audio_file_path):
        print(f"Error: File not found at '{audio_file_path}'")
        sys.exit(1)

    print(f"\n[Processing Recorded Audio File]: {audio_file_path}")
    print(f"[Language Selected]: {language}")

    with open(audio_file_path, "rb") as f:
        audio_bytes = f.read()

    service = PerceptionService()
    service.load_models()

    result = service.analyze(
        audio_bytes=audio_bytes,
        filename=os.path.basename(audio_file_path),
        language=language,
        channel="ivrs"
    )

    print("\n" + "=" * 80)
    print("  AI PERCEPTION VOICE TEST RESULT")
    print("=" * 80)
    print(f"➜ STT Transcript    : \"{result.model_predictions[0].name if result.model_predictions else 'N/A'}\"")
    print(f"➜ SVI Risk Score    : {result.svi.score} / 100")
    print(f"➜ Risk Tier         : {result.svi.risk_tier}")
    print(f"➜ Language Detected : {result.language.name} ({result.language.code})")
    print("\n➜ Risk Flags & Evidence Signals:")
    for flag in result.flags:
        print(f"   • [{flag.name.upper()}] Confidence: {flag.confidence*100:.1f}%")
        for sig in flag.signals:
            print(f"     - {sig}")

    print("\n" + "=" * 80)
    print("Complete JSON Output:")
    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
