"""
Audio Processing Utilities for Helpline STT and Signal Processing
"""

import os
import wave
import struct
import math
import numpy as np
from typing import Tuple

def generate_synthetic_audio(
    output_path: str,
    duration_sec: float = 3.0,
    sample_rate: int = 16000,
    frequency: float = 440.0,
    add_pauses: bool = True
) -> str:
    """
    Generates a synthetic WAV audio file for testing STT and acoustic features.
    
    Args:
        output_path: Path where wav file will be saved.
        duration_sec: Length of audio in seconds.
        sample_rate: Audio sampling frequency in Hz (default 16000).
        frequency: Base tone frequency in Hz (default 440.0 Hz).
        add_pauses: If True, inserts periodic silence intervals (pauses).
        
    Returns:
        Absolute file path to the generated WAV file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    num_samples = int(duration_sec * sample_rate)
    
    t = np.linspace(0, duration_sec, num_samples, False)
    # Generate pitch modulated tone + subtle harmonics
    signal = 0.5 * np.sin(2 * np.pi * frequency * t) + 0.2 * np.sin(2 * np.pi * (frequency * 1.5) * t)
    
    if add_pauses:
        # Create silence pause between 1.0s and 2.0s
        pause_mask = (t >= 1.0) & (t <= 2.0)
        signal[pause_mask] = 0.001 * np.random.randn(np.sum(pause_mask))
    
    # Scale to 16-bit PCM integer range
    audio_int16 = (signal * 32767).astype(np.int16)
    
    with wave.open(output_path, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
        
    return output_path

def get_audio_duration(file_path: str) -> float:
    """Returns the duration of a WAV file in seconds."""
    with wave.open(file_path, "rb") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        return frames / float(rate)
