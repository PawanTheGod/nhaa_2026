"""
CLI Entry Point for Acoustic Speech-Feature Extraction Module
==============================================================================
Usage:
    python -m perception.speech_features --audio samples/test.wav
==============================================================================
"""

import sys
import argparse
import json
from perception.speech_features.feature_extractor import extract_acoustic_features

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="NHAA 14566 / SIH 26093 - Acoustic Speech-Feature Extractor CLI"
    )
    parser.add_argument(
        "--audio",
        type=str,
        required=True,
        help="Path to input audio file (.wav, .mp3, .m4a, .flac)"
    )

    args = parser.parse_args()

    print("=" * 80)
    print(f"Extracting Acoustic Speech Features from file: {args.audio}")
    print("=" * 80)

    result = extract_acoustic_features(args.audio)

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
