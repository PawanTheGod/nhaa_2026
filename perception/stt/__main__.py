"""
CLI Entry Point for Speech-to-Text Module
==============================================================================
Usage:
    python -m perception.stt --audio samples/test.wav
    python -m perception.stt --audio samples/test.wav --language hi --model base
==============================================================================
"""

import sys
import argparse
import json
from perception.stt.stt_module import audio_to_transcript

def main():
    # Ensure Windows console uses UTF-8 encoding for Hindi/Tamil character printing
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="NHAA 14566 / SIH 26093 - Multilingual Speech-to-Text CLI"
    )
    parser.add_argument(
        "--audio",
        type=str,
        required=True,
        help="Path to input audio file (.wav, .mp3, .m4a, .flac)"
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Optional ISO language code (e.g., 'hi', 'en', 'ta')"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="tiny",
        help="Whisper model size ('tiny', 'base', 'small', 'medium', 'large')"
    )

    args = parser.parse_args()

    print("=" * 80)
    print(f"Executing STT Pipeline on file: {args.audio}")
    print("=" * 80)

    result = audio_to_transcript(
        audio_file=args.audio,
        language=args.language,
        model_name=args.model
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
