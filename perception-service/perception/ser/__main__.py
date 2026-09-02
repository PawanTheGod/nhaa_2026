"""
CLI Entry Point for Speech Emotion Recognition Module
==============================================================================
Usage:
    python -m perception.ser --audio samples/test.wav
    python -m perception.ser --audio samples/test.wav --model superb/wav2vec2-base-superb-er
==============================================================================
"""

import sys
import argparse
import json
from perception.ser.ser_module import audio_to_emotion, DEFAULT_EMOTION_MODEL

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="NHAA 14566 / SIH 26093 - Speech Emotion Recognition CLI"
    )
    parser.add_argument(
        "--audio",
        type=str,
        required=True,
        help="Path to input audio file (.wav, .mp3, .m4a, .flac)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_EMOTION_MODEL,
        help="Pretrained Hugging Face audio classification model checkpoint"
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=5,
        help="Number of top predictions to display (default 5)"
    )

    args = parser.parse_args()

    print("=" * 80)
    print(f"Executing Speech Emotion Recognition on file: {args.audio}")
    print("=" * 80)

    result = audio_to_emotion(
        audio_file=args.audio,
        model_name=args.model,
        top_k=args.top_k
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
