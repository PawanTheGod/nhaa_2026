"""
NHAA 14566 / SIH 26093 - STT Pipeline Demonstration Script
==============================================================================
Runs Speech-to-Text inference across English, Hindi, and Tamil test samples.
Prints structured perception output and MongoDB payload format.
==============================================================================
"""

import os
import sys
import json

# Ensure Windows console handles UTF-8 (Hindi/Tamil Indic scripts)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from utils.audio_utils import generate_synthetic_audio
from stt.stt_pipeline import SpeechToTextPipeline

def main():
    print("=" * 80)
    print("NHAA 14566 / SIH 26093 - AI Perception Layer: Step 1 (Speech-to-Text)")
    print("=" * 80)
    
    # 1. Generate test audio file
    test_audio = "sample_test_call.wav"
    print(f"\n[1] Generating sample audio file '{test_audio}' (3.0 sec, 16kHz WAV)...")
    generate_synthetic_audio(test_audio, duration_sec=3.0, sample_rate=16000, add_pauses=True)
    
    # 2. Initialize STT Pipeline
    print("\n[2] Initializing STT Pipeline (Whisper 'tiny' for fast execution)...")
    pipeline = SpeechToTextPipeline(model_size="tiny")

    # 3. Test across languages: Hindi, English, Tamil (Tested) and Marathi (Untested)
    test_languages = [("hi", "Hindi"), ("en", "English"), ("ta", "Tamil"), ("mr", "Marathi (Untested Benchmark)")]

    for lang_code, lang_name in test_languages:
        print(f"\n" + "-" * 60)
        print(f"Testing Transcription for Language: {lang_name} ({lang_code})")
        print("-" * 60)
        
        result = pipeline.transcribe(test_audio, language=lang_code if "(" not in lang_name else "mr")
        
        print(f"Transcript         : '{result.transcript}'")
        print(f"Language           : {result.language}")
        print(f"Validation Status  : {result.tested_status}")
        print(f"Confidence Score   : {result.confidence_score}")
        print(f"Audio Duration     : {result.duration_sec} s")
        print(f"Model Used         : {result.model_name}")
        print(f"Safety Disclaimer  : {result.safety_disclaimer}")
        print("\nMongoDB Document Payload:")
        print(json.dumps(result.to_mongo_dict(), indent=2, ensure_ascii=False))

    # Clean up test file
    if os.path.exists(test_audio):
        os.remove(test_audio)
        print(f"\n[Clean Up] Removed temporary test file '{test_audio}'.")

    print("\n" + "=" * 80)
    print("Step 1 (Speech-To-Text Pipeline) Execution Complete.")
    print("=" * 80)

if __name__ == "__main__":
    main()
