"""
Dataset Loader & Label Alignment Manager for SER Benchmarks (RAVDESS / CREMA-D)
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
"""

import os
import re
import glob
import pathlib
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

from utils.audio_utils import generate_synthetic_audio

# RAVDESS emotion code mapping
# Filename structure: 03-01-05-01-01-01-01.wav -> 3rd field '05' = angry
RAVDESS_EMOTION_MAP = {
    "01": "neutral",
    "02": "calm",
    "03": "happy",
    "04": "sad",
    "05": "angry",
    "06": "fearful",
    "07": "disgust",
    "08": "surprised"
}

# CREMA-D emotion code mapping
CREMA_EMOTION_MAP = {
    "NEU": "neutral",
    "HAP": "happy",
    "SAD": "sad",
    "ANG": "angry",
    "FEA": "fearful",
    "DIS": "disgust"
}

# Canonical model label aliases to ensure 1:1 alignment without silent merging
LABEL_ALIASES = {
    "fear": "fearful",
    "fearful": "fearful",
    "surprise": "surprised",
    "surprised": "surprised",
    "happiness": "happy",
    "happy": "happy",
    "sadness": "sad",
    "sad": "sad",
    "anger": "angry",
    "angry": "angry",
    "neutral": "neutral",
    "calm": "calm",
    "disgust": "disgust"
}

class BenchmarkDatasetLoader:
    """Loads and formats open SER benchmark datasets (RAVDESS / CREMA-D)."""

    def __init__(self, dataset_name: str = "RAVDESS"):
        self.dataset_name = dataset_name.upper()

    def parse_ravdess_filename(self, filepath: str) -> Optional[str]:
        """Extracts emotion label from RAVDESS filename format (03-01-XX-...)."""
        filename = os.path.basename(filepath)
        parts = filename.split("-")
        if len(parts) >= 3:
            emotion_code = parts[2]
            return RAVDESS_EMOTION_MAP.get(emotion_code)
        return None

    def parse_crema_filename(self, filepath: str) -> Optional[str]:
        """Extracts emotion label from CREMA-D filename format (1001_DFA_ANG_XX.wav)."""
        filename = os.path.basename(filepath)
        parts = filename.split("_")
        if len(parts) >= 3:
            code = parts[2].upper()
            return CREMA_EMOTION_MAP.get(code)
        return None

    def load_dataset(self, dataset_dir: str) -> List[Tuple[str, str]]:
        """
        Scans directory and returns list of (file_path, ground_truth_label).
        """
        samples = []
        if not os.path.exists(dataset_dir):
            return samples

        wav_files = glob.glob(os.path.join(dataset_dir, "**", "*.wav"), recursive=True)
        for path in wav_files:
            if self.dataset_name == "RAVDESS":
                label = self.parse_ravdess_filename(path)
            elif self.dataset_name == "CREMA-D" or self.dataset_name == "CREMAD":
                label = self.parse_crema_filename(path)
            else:
                label = None

            if label:
                samples.append((path, label))

        return samples


def generate_synthetic_benchmark_dataset(
    target_dir: str = "perception/evaluation/samples_benchmark",
    samples_per_class: int = 3
) -> List[Tuple[str, str]]:
    """
    Generates synthetic RAVDESS-formatted WAV files for zero-leakage pipeline verification.
    """
    os.makedirs(target_dir, exist_ok=True)
    samples = []
    
    # Generate 5 RAVDESS emotion categories
    emotion_codes = [
        ("01", "neutral", 220.0),
        ("03", "happy", 350.0),
        ("04", "sad", 180.0),
        ("05", "angry", 440.0),
        ("06", "fearful", 380.0)
    ]

    idx = 1
    for code, label_name, freq in emotion_codes:
        for s in range(samples_per_class):
            filename = f"03-01-{code}-01-01-01-{idx:02d}.wav"
            filepath = os.path.join(target_dir, filename)
            generate_synthetic_audio(
                filepath,
                duration_sec=2.5,
                frequency=freq,
                add_pauses=(label_name in ("sad", "fearful"))
            )
            samples.append((filepath, label_name))
            idx += 1

    return samples
