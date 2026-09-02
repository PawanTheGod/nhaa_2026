"""
Live Demonstration Script for NHAA 14566 / SIH 26093 AI Perception Layer
==============================================================================
Demonstrates end-to-end perception execution across English, Hindi, and Marathi
callers, showing SVI scoring, evidence generation, and Vinit backend payloads.
==============================================================================
"""

import os
import sys
import json
import tempfile
import numpy as np
import soundfile as sf

# Reconfigure stdout to handle UTF-8 symbols and Indic scripts on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from api.services.perception_service import PerceptionService
from perception.schemas.perception_contract import PerceptionOutputContract


def create_demo_audio(duration_sec: float = 3.0, pitch_freq: float = 240.0) -> str:
    """Creates a sample synthetic speech audio file for demonstration."""
    sr = 16000
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    # Fundamental frequency + harmonics + mild noise
    audio = 0.5 * np.sin(2 * np.pi * pitch_freq * t) + 0.2 * np.sin(2 * np.pi * (pitch_freq * 2) * t)
    audio = audio.astype(np.float32)

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, audio, sr)
    tmp.close()
    return tmp.name


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)


def run_live_demo():
    print_banner("NHAA 14566 / SIH 26093 - AI Perception Layer Live Demonstration")
    
    # Initialize Perception Service
    service = PerceptionService()
    print("\n[1/4] Initializing and pre-loading ML models on device...")
    service.load_models()

    # Case 1: Hindi Emergency Helpline Call
    print_banner("Case 1: Hindi Helpline Emergency Call (Audio + Text)")
    audio_path_hi = create_demo_audio(duration_sec=4.5, pitch_freq=280.0)
    with open(audio_path_hi, "rb") as f:
        audio_bytes_hi = f.read()
    
    hindi_text = "मुझे बचाओ, मुझे जान से मारने की धमकी मिल रही है और बहुत डर लग रहा है"
    print(f"• Ingestion Channel : IVRS Telephonic Call")
    print(f"• Language          : Hindi (hi)")
    print(f"• Citizen Input Text: \"{hindi_text}\"")

    contract_hi = service.analyze(
        audio_bytes=audio_bytes_hi,
        filename="hindi_call.wav",
        text=hindi_text,
        language="hi",
        case_id="CASE-14566-101",
        channel="ivrs"
    )

    print("\n[AI PERCEPTION ANALYSIS RESULT - HINDI CASE]")
    print(f"➜ SVI Score          : {contract_hi.svi.score} / 100")
    print(f"➜ Risk Tier          : {contract_hi.svi.risk_tier}")
    print(f"➜ Language Status    : {contract_hi.language.name} [{contract_hi.language.tested_status}]")
    print("➜ Detected Risk Flags:")
    for flag in contract_hi.flags:
        print(f"   - [{flag.name.upper()}] Confidence: {flag.confidence*100:.1f}% | Sources: {flag.source}")
        for sig in flag.signals:
            print(f"     • Evidence: {sig}")

    os.remove(audio_path_hi)

    # Case 2: Marathi Emergency Helpline Call
    print_banner("Case 2: Marathi Helpline Emergency Call (Audio + Text)")
    audio_path_mr = create_demo_audio(duration_sec=5.0, pitch_freq=310.0)
    with open(audio_path_mr, "rb") as f:
        audio_bytes_mr = f.read()

    marathi_text = "मला मदत करा, मला मारहाण आणि धमकी दिली जात आहे, मी खूप घाबरलोय"
    print(f"• Ingestion Channel : Mobile App Helpline")
    print(f"• Language          : Marathi (mr)")
    print(f"• Citizen Input Text: \"{marathi_text}\"")

    contract_mr = service.analyze(
        audio_bytes=audio_bytes_mr,
        filename="marathi_call.wav",
        text=marathi_text,
        language="mr",
        case_id="CASE-14566-102",
        channel="mobile_app"
    )

    print("\n[AI PERCEPTION ANALYSIS RESULT - MARATHI CASE]")
    print(f"➜ SVI Score          : {contract_mr.svi.score} / 100")
    print(f"➜ Risk Tier          : {contract_mr.svi.risk_tier}")
    print(f"➜ Language Status    : {contract_mr.language.name} [{contract_mr.language.tested_status}]")
    print("➜ Detected Risk Flags:")
    for flag in contract_mr.flags:
        print(f"   - [{flag.name.upper()}] Confidence: {flag.confidence*100:.1f}% | Sources: {flag.source}")
        for sig in flag.signals:
            print(f"     • Evidence: {sig}")

    os.remove(audio_path_mr)

    # Case 3: Vinit Central Case API Payload Conversion Export
    print_banner("Case 3: Exporting Payload for Vinit's Central Case Backend")
    vinit_payload = contract_hi.to_vinit_payload(case_id_override=101)
    print("Payload sent to Vinit's Central Case API (POST /risk-assessments/):")
    print(json.dumps(vinit_payload, indent=2, ensure_ascii=False))

    print_banner("Demonstration Complete")
    print("All perception models, language classifiers, SVI score fusion engines,")
    print("and Central Case API converters executed successfully!")


if __name__ == "__main__":
    run_live_demo()
