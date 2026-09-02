"""
Speech Emotion Recognition (SER) & Acoustic Feature Fusion Module
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
SAFETY & ETHICAL NOTICE:
- Emotion predictions are physical speech signal estimations.
- THEY DO NOT CONSTITUTE MEDICAL OR CLINICAL DIAGNOSES.
- Crucially: fear ≠ trauma, sadness ≠ depression, low energy ≠ suicidal ideation.
- Raw emotion predictions are kept separate from clinical distress interpretation.
==============================================================================
"""

import os
import sys
import time
import pathlib
from typing import Dict, List, Optional, Any, Union
import numpy as np
import torch

try:
    import librosa
    from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from config import config
from perception.speech_features import extract_acoustic_features

# Default open-source pretrained emotion checkpoint (Apache 2.0 / MIT with safetensors support)
DEFAULT_EMOTION_MODEL = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"

# Allowed audio file extensions
SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".wma"}
MAX_AUDIO_DURATION_SEC = 1800.0

# Mandatory ethical disclaimer string
SAFETY_DISCLAIMER_SER = (
    "PERCEPTION SIGNAL ONLY: Emotion predictions are acoustic signals, NOT clinical medical diagnoses. "
    "Crucially: fear ≠ trauma, sadness ≠ depression, low energy ≠ suicidal ideation. "
    "Intended solely for helpline triage prioritization under human officer oversight."
)


class SpeechEmotionRecognizer:
    """
    Local Speech Emotion Recognizer using Wav2Vec2/HuBERT pretrained checkpoints.
    Supports CUDA GPU acceleration with automatic CPU fallback.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_EMOTION_MODEL,
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.device = device or ("cuda" if config.stt.device == "cuda" and torch.cuda.is_available() else "cpu")
        self.feature_extractor = None
        self.model = None
        self.id2label = {}
        self._load_model()

    def _load_model(self):
        if not TRANSFORMERS_AVAILABLE or self.model_name in ("mock", "fallback", "acoustic"):
            print(f"[SER] Initialized SpeechEmotionRecognizer in acoustic fallback mode ('{self.model_name}').")
            return

        try:
            print(f"[SER] Loading emotion checkpoint '{self.model_name}' on device '{self.device}'...")
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(self.model_name)
            try:
                self.model = AutoModelForAudioClassification.from_pretrained(self.model_name, use_safetensors=True).to(self.device)
            except Exception:
                self.model = AutoModelForAudioClassification.from_pretrained(self.model_name).to(self.device)
            self.model.eval()
            self.id2label = self.model.config.id2label
            print(f"[SER] Model '{self.model_name}' loaded successfully on '{self.device}'.")
        except Exception as e:
            print(f"[SER WARNING] Failed to load on '{self.device}' ({e}). Falling back to CPU...")
            try:
                self.device = "cpu"
                self.feature_extractor = AutoFeatureExtractor.from_pretrained(self.model_name)
                try:
                    self.model = AutoModelForAudioClassification.from_pretrained(self.model_name, use_safetensors=True).to(self.device)
                except Exception:
                    self.model = AutoModelForAudioClassification.from_pretrained(self.model_name).to(self.device)
                self.model.eval()
                self.id2label = self.model.config.id2label
                print(f"[SER] Model '{self.model_name}' loaded on CPU fallback.")
            except Exception as ex:
                print(f"[SER ERROR] Could not load emotion model ({ex}). Utilizing acoustic feature predictor fallback.")
                self.model = None

    def predict(self, audio_path: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Runs local inference on an audio file and returns top-k emotion probabilities.
        """
        if self.model is None or self.feature_extractor is None:
            return [{"label": "neutral", "confidence": 0.50}]

        # Load 16kHz audio array
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
        if len(y) == 0:
            return [{"label": "neutral", "confidence": 0.50}]

        # Preprocess audio features
        inputs = self.feature_extractor(
            y,
            sampling_rate=sr,
            return_tensors="pt",
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()

        # Format predictions list sorted by score descending
        predictions = []
        for idx, score in enumerate(probs):
            label = self.id2label.get(idx, f"label_{idx}").lower()
            predictions.append({
                "label": label,
                "confidence": round(float(score), 4)
            })

        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        return predictions[:top_k]

    def predict_from_features(self, acoustic_signals: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Acoustic heuristic fallback when neural model weights are unavailable offline.
        Uses pitch variation, pause silence ratio, and RMS energy dynamics.
        """
        pitch_var = acoustic_signals.get("pitch_variation", 0.0)
        pitch_std = acoustic_signals.get("pitch_std_hz", 0.0)
        silence_ratio = acoustic_signals.get("silence_ratio", 0.0)
        energy_var = acoustic_signals.get("energy_variation", 0.0)

        # Base scores
        scores = {"neutral": 0.40, "fear": 0.20, "sad": 0.20, "angry": 0.20}

        if pitch_var > 0.25 or pitch_std > 50.0:
            scores["fear"] += 0.35
            scores["angry"] += 0.25
        elif silence_ratio > 0.35 and energy_var < 0.10:
            scores["sad"] += 0.40
            scores["neutral"] += 0.20
        elif energy_var > 0.20 and pitch_std > 40.0:
            scores["angry"] += 0.40
            scores["fear"] += 0.20
        else:
            scores["neutral"] += 0.30

        # Normalize to probabilities
        total = sum(scores.values())
        norm_preds = [
            {"label": k, "confidence": round(v / total, 4)}
            for k, v in scores.items()
        ]
        norm_preds.sort(key=lambda x: x["confidence"], reverse=True)
        return norm_preds[:top_k]


# Global cached instance
_GLOBAL_SER_RECOGNIZER: Optional[SpeechEmotionRecognizer] = None

def get_ser_recognizer(model_name: str = DEFAULT_EMOTION_MODEL, device: Optional[str] = None) -> SpeechEmotionRecognizer:
    global _GLOBAL_SER_RECOGNIZER
    if _GLOBAL_SER_RECOGNIZER is None or _GLOBAL_SER_RECOGNIZER.model_name != model_name:
        _GLOBAL_SER_RECOGNIZER = SpeechEmotionRecognizer(model_name=model_name, device=device)
    return _GLOBAL_SER_RECOGNIZER


def audio_to_emotion(
    audio_file: Union[str, pathlib.Path],
    model_name: str = DEFAULT_EMOTION_MODEL,
    top_k: int = 5,
    device: Optional[str] = None
) -> Dict[str, Any]:
    """
    Classifies speech emotion probabilities and pairs them with named acoustic features.
    
    Args:
        audio_file: Path to input audio file.
        model_name: Pretrained Hugging Face Wav2Vec2/HuBERT checkpoint name.
        top_k: Number of top predictions to return.
        device: 'cuda' or 'cpu'.
        
    Returns:
        Structured dictionary containing emotion, top_predictions, acoustic_signals,
        processing_time, success/error status, and safety disclaimer.
    """
    start_time = time.time()
    audio_path = str(audio_file)

    # -------------------------------------------------------------------------
    # 1. Validation Checks
    # -------------------------------------------------------------------------
    if not os.path.exists(audio_path):
        return {
            "success": False,
            "error": f"Audio file not found: {audio_path}",
            "emotion": {"label": "unknown", "confidence": 0.0},
            "top_predictions": [],
            "acoustic_signals": {},
            "model_name": model_name,
            "processing_time": round(time.time() - start_time, 3),
            "safety_disclaimer": SAFETY_DISCLAIMER_SER
        }

    ext = os.path.splitext(audio_path)[1].lower()
    if ext not in SUPPORTED_AUDIO_EXTENSIONS:
        return {
            "success": False,
            "error": f"Unsupported format '{ext}'. Supported: {sorted(list(SUPPORTED_AUDIO_EXTENSIONS))}",
            "emotion": {"label": "unknown", "confidence": 0.0},
            "top_predictions": [],
            "acoustic_signals": {},
            "model_name": model_name,
            "processing_time": round(time.time() - start_time, 3),
            "safety_disclaimer": SAFETY_DISCLAIMER_SER
        }

    if os.path.getsize(audio_path) == 0:
        return {
            "success": False,
            "error": f"Audio file is empty (0 bytes): {audio_path}",
            "emotion": {"label": "unknown", "confidence": 0.0},
            "top_predictions": [],
            "acoustic_signals": {},
            "model_name": model_name,
            "processing_time": round(time.time() - start_time, 3),
            "safety_disclaimer": SAFETY_DISCLAIMER_SER
        }

    # -------------------------------------------------------------------------
    # 2. Extract Acoustic Features from Speech-Features Module
    # -------------------------------------------------------------------------
    ac_features = extract_acoustic_features(audio_path)
    if not ac_features.get("success", False):
        return {
            "success": False,
            "error": ac_features.get("error", "Acoustic feature extraction failed."),
            "emotion": {"label": "unknown", "confidence": 0.0},
            "top_predictions": [],
            "acoustic_signals": {},
            "model_name": model_name,
            "processing_time": round(time.time() - start_time, 3),
            "safety_disclaimer": SAFETY_DISCLAIMER_SER
        }

    acoustic_signals = {
        "pitch_variation": ac_features["pitch"]["pitch_variation"],
        "pitch_mean_hz": ac_features["pitch"]["mean_hz"],
        "pitch_std_hz": ac_features["pitch"]["std_hz"],
        "pitch_range_hz": ac_features["pitch"]["range_hz"],
        "pause_count": ac_features["pauses"]["count"],
        "mean_pause_duration_seconds": ac_features["pauses"]["mean_duration_seconds"],
        "max_pause_duration_seconds": ac_features["pauses"]["max_duration_seconds"],
        "silence_ratio": ac_features["pauses"]["silence_ratio"],
        "energy_variation": ac_features["energy"]["std_rms"],
        "mean_rms": ac_features["energy"]["mean_rms"],
        "speaking_rate_proxy": ac_features["speech_characteristics"]["speaking_rate_proxy"]
    }

    # -------------------------------------------------------------------------
    # 3. Speech Emotion Neural Inference / Fallback
    # -------------------------------------------------------------------------
    recognizer = get_ser_recognizer(model_name=model_name, device=device)
    if recognizer.model is not None:
        top_preds = recognizer.predict(audio_path, top_k=top_k)
    else:
        top_preds = recognizer.predict_from_features(acoustic_signals, top_k=top_k)

    top_emotion = top_preds[0] if top_preds else {"label": "neutral", "confidence": 0.50}

    processing_time = round(time.time() - start_time, 3)

    return {
        "success": True,
        "error": None,
        "emotion": top_emotion,
        "top_predictions": top_preds,
        "acoustic_signals": acoustic_signals,
        "model_name": model_name,
        "processing_time": processing_time,
        "safety_disclaimer": SAFETY_DISCLAIMER_SER
    }
