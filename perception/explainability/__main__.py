"""
CLI Entry Point for Explainability / Evidence Generation Module
==============================================================================
Usage:
    python -m perception.explainability --audio samples/test.wav --text "मुझे धमकी मिल रही है"
==============================================================================
"""

import sys
import argparse
import json

from perception.stt import audio_to_transcript
from perception.ser import audio_to_emotion
from perception.speech_features import extract_acoustic_features
from perception.text_distress import text_to_distress_flags
from perception.explainability.evidence_builder import build_unified_evidence_report

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="NHAA 14566 / SIH 26093 - Explainability & Evidence CLI"
    )
    parser.add_argument("--audio", type=str, default=None, help="Path to input audio file")
    parser.add_argument("--text", type=str, default=None, help="Input citizen text / transcript")
    parser.add_argument("--language", type=str, default="hi", help="Language code ('hi', 'en', 'ta')")

    args = parser.parse_args()

    print("=" * 80)
    print("Executing Explainability & Unified Evidence Extraction")
    print("=" * 80)

    stt_res = None
    ser_res = None
    ac_res = None
    text_res = None

    if args.audio:
        print(f"[Speech Pipeline] Processing audio file: {args.audio}...")
        stt_res = audio_to_transcript(args.audio, language=args.language, model_name="tiny")
        ser_res = audio_to_emotion(args.audio, model_name="mock")
        ac_res = extract_acoustic_features(args.audio)

    if args.text:
        print(f"[Text Pipeline] Processing citizen text input...")
        text_res = text_to_distress_flags(args.text, language=args.language)

    report = build_unified_evidence_report(
        stt_result=stt_res,
        ser_result=ser_res,
        speech_features_result=ac_res,
        text_distress_result=text_res
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
