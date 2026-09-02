"""
CLI Entry Point for Multilingual Text Distress Classification Module
==============================================================================
Usage:
    python -m perception.text_distress --text "मुझे जान से मारने की धमकी मिल रही है"
    python -m perception.text_distress --text "I feel terrified and hopeless" --language en
==============================================================================
"""

import sys
import argparse
import json
from perception.text_distress.text_classifier import text_to_distress_flags

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="NHAA 14566 / SIH 26093 - Multilingual Text Distress Classification CLI"
    )
    parser.add_argument(
        "--text",
        type=str,
        required=True,
        help="Input text string (Hindi, English, Tamil)"
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Optional ISO language code ('hi', 'en', 'ta')"
    )
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="Use OpenRouter LLM fallback path"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Executing Multilingual Text Distress Classification")
    print("=" * 80)

    result = text_to_distress_flags(
        text=args.text,
        language=args.language,
        use_fallback=args.fallback
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
