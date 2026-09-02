"""
Random Voice Synthesizer & Perception Layer Tester
==============================================================================
Generates random synthetic speech audio clips with varied pitch shaking,
pause lengths, and vocal energy profiles, saving real WAV files to disk
and running them live through the AI Perception Layer.
==============================================================================
"""

import os
import sys
import json
import time
import pathlib
import numpy as np
import soundfile as sf

# Reconfigure stdout for Windows UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from api.services.perception_service import PerceptionService


def generate_random_voice_clip(filename: str, duration_sec: float, base_freq: float, pause_at_sec: float = 1.5):
    """
    Generates a realistic synthetic speech audio waveform with pitch modulation
    and unvoiced pause intervals, saving it to disk as a 16kHz MONO WAV file.
    """
    sr = 16000
    total_samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, total_samples, endpoint=False)

    # Pitch modulation (frequency modulation simulating speech cadence and tremolo)
    freq_mod = base_freq + 25.0 * np.sin(2 * np.pi * 3.5 * t) + 15.0 * np.cos(2 * np.pi * 7.2 * t)
    phase = 2 * np.pi * np.cumsum(freq_mod) / sr

    # Formant harmonics (simulating vocal tract resonances)
    audio = 0.5 * np.sin(phase) + 0.25 * np.sin(2 * phase) + 0.12 * np.sin(3 * phase)

    # Insert unvoiced pause interval (silence/hesitation)
    pause_start_idx = int(pause_at_sec * sr)
    pause_end_idx = min(total_samples, pause_start_idx + int(1.8 * sr))
    audio[pause_start_idx:pause_end_idx] = 0.0

    # Apply speech envelope (fade in/out)
    envelope = np.ones(total_samples, dtype=np.float32)
    fade_len = int(0.05 * sr)
    envelope[:fade_len] = np.linspace(0, 1, fade_len)
    envelope[-fade_len:] = np.linspace(1, 0, fade_len)

    audio = (audio * envelope).astype(np.float32)
    sf.write(filename, audio, sr)
    return filename


def run_random_voice_tests():
    print("=" * 80)
    print("  GENERATING RANDOM SYNTHETIC VOICE AUDIO CLIPS & TESTING LIVE AI PERCEPTION")
    print("=" * 80)

    # Initialize Service
    service = PerceptionService()
    service.load_models()

    # Generate 3 Random Synthetic Voice Recordings
    voice_clips = [
        {
            "id": 1,
            "filename": "random_voice_clip_1.wav",
            "title": "Voice 1: High-Pitch Panicked Voice (Hindi)",
            "duration": 4.5,
            "pitch_freq": 310.0,
            "pause_at": 1.2,
            "text": "मुझे बचाओ, मुझे डर लग रहा है और धमकी मिल रही है",
            "lang": "hi"
        },
        {
            "id": 2,
            "filename": "random_voice_clip_2.wav",
            "title": "Voice 2: Agitated Shouting Voice (Marathi)",
            "duration": 5.0,
            "pitch_freq": 260.0,
            "pause_at": 2.0,
            "text": "मला मदत करा, मला मारहाण आणि धमकी दिली जात आहे",
            "lang": "mr"
        },
        {
            "id": 3,
            "filename": "random_voice_clip_3.wav",
            "title": "Voice 3: Trembling Distress Voice (English)",
            "duration": 4.0,
            "pitch_freq": 180.0,
            "pause_at": 1.0,
            "text": "Help me, I am terrified and in extreme danger",
            "lang": "en"
        }
    ]

    for clip in voice_clips:
        print(f"\n" + "-" * 80)
        print(f"➜ Generating {clip['title']}...")
        wav_path = generate_random_voice_clip(
            filename=clip["filename"],
            duration_sec=clip["duration"],
            base_freq=clip["pitch_freq"],
            pause_at_sec=clip["pause_at"]
        )
        print(f"  Saved Audio File : {os.path.abspath(wav_path)} ({clip['duration']}s @ {clip['pitch_freq']}Hz)")

        with open(wav_path, "rb") as f:
            audio_bytes = f.read()

        t0 = time.time()
        result = service.analyze(
            audio_bytes=audio_bytes,
            filename=clip["filename"],
            text=clip["text"],
            language=clip["lang"],
            case_id=f"RANDOM-VOICE-{clip['id']}",
            channel="ivrs"
        )
        latency = (time.time() - t0) * 1000.0

        print(f"\n[AI PERCEPTION LIVE ANALYSIS RESULTS - {clip['lang'].upper()}]")
        print(f"  • Ingestion Channel  : IVRS Telephonic Call")
        print(f"  • Analysis Latency   : {latency:.1f} ms ({latency/1000.0:.3f} seconds)")
        print(f"  • Language Detected  : {result.language.name} [{result.language.tested_status}]")
        print(f"  • SVI Score          : {result.svi.score} / 100")
        print(f"  • Assigned Risk Tier : {result.svi.risk_tier}")

        print("\n  • Acoustic Voice Signals Extracted:")
        for raw in result.raw_measurements:
            if raw.source == "audio":
                print(f"    - [{raw.name}] {raw.value} {raw.unit}")

        print("\n  • Detected Risk Flags & Auditable Evidence:")
        for flag in result.flags:
            print(f"    - [{flag.name.upper()}] Confidence: {flag.confidence*100:.1f}% | Modality: {flag.source}")
            for sig in flag.signals:
                print(f"      * {sig}")

    print("\n" + "=" * 80)
    print("  ALL 3 RANDOM VOICE CLIPS GENERATED & TESTED SUCCESSFULLY!")
    print("  Audio files saved on disk:")
    for clip in voice_clips:
        uri_path = pathlib.Path(clip['filename']).resolve().as_uri()
        print(f"  • {uri_path}")
    print("=" * 80)


if __name__ == "__main__":
    run_random_voice_tests()
