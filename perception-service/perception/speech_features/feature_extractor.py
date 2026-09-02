"""
Interpretable Acoustic Speech-Feature Extraction Module
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
SAFETY & ETHICAL MANDATE:
- Extracts structural acoustic measurements (pitch variation, pause patterns, energy).
- DOES NOT CONSTITUTE A CLINICAL DIAGNOSIS OR PROVE PSYCHOLOGICAL TRAUMA.
- Perception signals are provided for triage decision assistance under human oversight.
==============================================================================
"""

import os
import math
import time
import pathlib
from typing import Dict, List, Optional, Any, Union
import numpy as np

import librosa

from config import config

# Supported audio extensions
SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".wma"}

# Maximum audio duration threshold (seconds)
MAX_AUDIO_DURATION_SEC = 1800.0

# Minimum threshold for pause detection in seconds (ignore micro-stops between consonants)
MIN_PAUSE_DURATION_SEC = 0.20

class AcousticFeatureExtractor:
    """
    Extracts pitch (F0), pause patterns, RMS energy dynamics, and spectral features
    from raw audio signals using librosa and numpy.
    """

    def __init__(self, sample_rate: int = 16000, top_db: float = 25.0):
        self.sample_rate = sample_rate
        self.top_db = top_db  # Energy threshold in dB below top energy for silence detection

    def extract(self, audio_file: Union[str, pathlib.Path]) -> Dict[str, Any]:
        """
        Extracts acoustic features from an audio file.
        
        Args:
            audio_file: Path to audio file (.wav, .mp3, .flac, etc.)
            
        Returns:
            Structured dictionary containing pitch, energy, pause, and speech characteristics metrics.
        """
        start_time = time.time()
        audio_path = str(audio_file)

        # ---------------------------------------------------------------------
        # 1. Validation Checks
        # ---------------------------------------------------------------------
        if not os.path.exists(audio_path):
            return self._build_error_response(f"Audio file not found: {audio_path}", start_time)

        ext = os.path.splitext(audio_path)[1].lower()
        if ext not in SUPPORTED_AUDIO_EXTENSIONS:
            return self._build_error_response(
                f"Unsupported format '{ext}'. Supported: {sorted(list(SUPPORTED_AUDIO_EXTENSIONS))}",
                start_time
            )

        if os.path.getsize(audio_path) == 0:
            return self._build_error_response(f"Audio file is empty (0 bytes): {audio_path}", start_time)

        # Load audio using librosa
        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
        except Exception as e:
            return self._build_error_response(f"Failed to load audio file: {e}", start_time)

        if len(y) == 0:
            return self._build_error_response("Audio buffer is empty after loading.", start_time)

        total_duration = float(len(y) / sr)

        if total_duration > MAX_AUDIO_DURATION_SEC:
            return self._build_error_response(
                f"Audio duration ({total_duration:.1f}s) exceeds maximum threshold ({MAX_AUDIO_DURATION_SEC}s)",
                start_time
            )

        # ---------------------------------------------------------------------
        # 2. Pitch Extraction (F0 - Probabilistic YIN Algorithm)
        # ---------------------------------------------------------------------
        try:
            # F0 fundamental frequency tracking between 50 Hz and 500 Hz (human vocal range)
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                fmin=librosa.note_to_hz('C2'),  # ~65 Hz
                fmax=librosa.note_to_hz('C7'),  # ~2093 Hz
                sr=sr
            )
            valid_f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])
        except Exception:
            valid_f0 = np.array([])

        if len(valid_f0) > 0:
            mean_hz = float(np.mean(valid_f0))
            median_hz = float(np.median(valid_f0))
            min_hz = float(np.min(valid_f0))
            max_hz = float(np.max(valid_f0))
            std_hz = float(np.std(valid_f0))
            range_hz = float(max_hz - min_hz)
            pitch_var = float(std_hz / mean_hz) if mean_hz > 0 else 0.0
        else:
            mean_hz = median_hz = min_hz = max_hz = std_hz = range_hz = pitch_var = 0.0

        # ---------------------------------------------------------------------
        # 3. Energy & Loudness Dynamics (RMS)
        # ---------------------------------------------------------------------
        rms = librosa.feature.rms(y=y)[0]
        mean_rms = float(np.mean(rms)) if len(rms) > 0 else 0.0
        std_rms = float(np.std(rms)) if len(rms) > 0 else 0.0
        max_rms = float(np.max(rms)) if len(rms) > 0 else 0.0
        mean_energy = float(np.mean(rms ** 2)) if len(rms) > 0 else 0.0

        # ---------------------------------------------------------------------
        # 4. Speech Activity & Pause Patterns
        # ---------------------------------------------------------------------
        # Split non-silent intervals using energy thresholding (top_db)
        intervals = librosa.effects.split(y, top_db=self.top_db)
        
        voiced_samples = sum(end - start for start, end in intervals) if len(intervals) > 0 else 0
        voiced_duration = float(voiced_samples / sr)
        silence_duration = max(0.0, total_duration - voiced_duration)
        silence_ratio = float(silence_duration / total_duration) if total_duration > 0 else 0.0

        # Extract pause gaps between non-silent speech intervals
        pause_durations = []
        if len(intervals) > 1:
            for i in range(len(intervals) - 1):
                prev_end = intervals[i][1]
                next_start = intervals[i + 1][0]
                gap_sec = float((next_start - prev_end) / sr)
                if gap_sec >= MIN_PAUSE_DURATION_SEC:
                    pause_durations.append(gap_sec)
        elif len(intervals) == 0:
            # Entire file is silence
            pause_durations.append(total_duration)

        pause_count = len(pause_durations)
        mean_pause_dur = float(np.mean(pause_durations)) if pause_count > 0 else 0.0
        max_pause_dur = float(np.max(pause_durations)) if pause_count > 0 else 0.0

        # ---------------------------------------------------------------------
        # 5. Basic Speech Characteristics & Proxies
        # ---------------------------------------------------------------------
        zcr = librosa.feature.zero_crossing_rate(y=y)[0]
        mean_zcr = float(np.mean(zcr)) if len(zcr) > 0 else 0.0

        # Speaking rate proxy: voiced bursts / second of active speech
        speaking_rate_proxy = (
            round(len(intervals) / voiced_duration, 2)
            if voiced_duration > 0.5 else 0.0
        )

        processing_time = round(time.time() - start_time, 3)

        return {
            "success": True,
            "error": None,
            "duration_seconds": round(total_duration, 2),
            "pitch": {
                "mean_hz": round(mean_hz, 2),
                "median_hz": round(median_hz, 2),
                "min_hz": round(min_hz, 2),
                "max_hz": round(max_hz, 2),
                "std_hz": round(std_hz, 2),
                "range_hz": round(range_hz, 2),
                "pitch_variation": round(pitch_var, 4)
            },
            "energy": {
                "mean_rms": round(mean_rms, 4),
                "std_rms": round(std_rms, 4),
                "max_rms": round(max_rms, 4),
                "mean_energy": round(mean_energy, 6)
            },
            "pauses": {
                "count": pause_count,
                "mean_duration_seconds": round(mean_pause_dur, 2),
                "max_duration_seconds": round(max_pause_dur, 2),
                "silence_duration_seconds": round(silence_duration, 2),
                "voiced_duration_seconds": round(voiced_duration, 2),
                "silence_ratio": round(silence_ratio, 4)
            },
            "speech_characteristics": {
                "zero_crossing_rate_mean": round(mean_zcr, 4),
                "speaking_rate_proxy": speaking_rate_proxy
            },
            "processing_time": processing_time,
            "safety_disclaimer": config.safety.medical_disclaimer
        }

    def _build_error_response(self, error_msg: str, start_time: float) -> Dict[str, Any]:
        return {
            "success": False,
            "error": error_msg,
            "duration_seconds": 0.0,
            "pitch": {
                "mean_hz": 0.0, "median_hz": 0.0, "min_hz": 0.0,
                "max_hz": 0.0, "std_hz": 0.0, "range_hz": 0.0, "pitch_variation": 0.0
            },
            "energy": {
                "mean_rms": 0.0, "std_rms": 0.0, "max_rms": 0.0, "mean_energy": 0.0
            },
            "pauses": {
                "count": 0, "mean_duration_seconds": 0.0, "max_duration_seconds": 0.0,
                "silence_duration_seconds": 0.0, "voiced_duration_seconds": 0.0, "silence_ratio": 0.0
            },
            "speech_characteristics": {
                "zero_crossing_rate_mean": 0.0, "speaking_rate_proxy": 0.0
            },
            "processing_time": round(time.time() - start_time, 3),
            "safety_disclaimer": config.safety.medical_disclaimer
        }

# Global helper function
def extract_acoustic_features(audio_file: Union[str, pathlib.Path]) -> Dict[str, Any]:
    """Convenience function to extract acoustic features from an audio file."""
    extractor = AcousticFeatureExtractor()
    return extractor.extract(audio_file)
