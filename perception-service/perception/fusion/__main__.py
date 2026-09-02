"""
CLI Entry Point for Perception-to-SVI Fusion Engine
==============================================================================
Usage:
    python -m perception.fusion --audio samples/test.wav --text "मुझे धमकी मिल रही है"
==============================================================================
"""

import sys
import argparse
import json

from perception.stt import audio_to_transcript
from perception.ser import audio_to_emotion
from perception.speech_features import extract_acoustic_features
from perception.text_distress import text_to_distress_flags
from perception.fusion.svi_engine import compute_perception_fusion

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="NHAA 14566 / SIH 26093 - Multimodal Perception Fusion & SVI Aggregation CLI"
    )
    parser.add_argument("--audio", type=str, default=None, help="Path to input audio file")
    parser.add_argument("--text", type=str, default=None, help="Input citizen text / transcript")
    parser.add_argument("--language", type=str, default="hi", help="ISO language code ('hi', 'en', 'ta')")
    parser.add_argument("--case_id", type=str, default="CASE-14566-DEMO", help="Optional Central Case API Case ID")

    args = parser.parse_args()

    print("=" * 80)
    print("Executing Multimodal Perception-to-SVI Aggregation Engine")
    print("=" * 80)

    stt_res = None
    ser_res = None
    ac_res = None
    text_res = None

    if args.audio:
        print(f"[Audio Processing] Running Whisper STT, Wav2Vec2 SER & Acoustic Analysis on '{args.audio}'...")
        stt_res = audio_to_transcript(args.audio, language=args.language, model_name="tiny")
        ser_res = audio_to_emotion(args.audio, model_name="mock")
        ac_res = extract_acoustic_features(args.audio)

    if args.text:
        print(f"[Text Processing] Running Text Distress Classifier on input text...")
        text_res = text_to_distress_flags(args.text, language=args.language)

    payload = compute_perception_fusion(
        stt_result=stt_res,
        ser_result=ser_res,
        speech_features_result=ac_res,
        text_distress_result=text_res,
        case_id=args.case_id
    )

    print(json.dumps(payload, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
