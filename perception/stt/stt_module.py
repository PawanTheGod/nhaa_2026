"""
Multilingual Speech-to-Text (STT) Module
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Provides local, privacy-compliant Speech-To-Text transcription for helpline
audio recordings (Hindi, English, Tamil, and extensible Indic languages).
==============================================================================
"""

import os
import sys
import math
import time
import pathlib
from typing import Dict, List, Optional, Any, Union
import numpy as np

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

from config import config, TESTED_LANGUAGES, UNTESTED_LANGUAGES

# Allowed audio file extensions
SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".wma"}

# Maximum audio duration threshold in seconds (e.g. 30 minutes)
MAX_AUDIO_DURATION_SEC = 1800.0


def validate_audio_file(audio_bytes: bytes, filename: Optional[str] = None) -> tuple[bool, str]:
    """Validates uploaded audio file bytes, size, format, and minimum length."""
    if not audio_bytes or len(audio_bytes) < 4:
        return False, "Audio file is empty or missing data bytes."
    
    if len(audio_bytes) < 400:  # < ~0.05s of audio header
        return False, "Audio duration is too short for reliable perception analysis."

    if filename:
        ext = pathlib.Path(filename).suffix.lower()
        if ext and ext not in SUPPORTED_AUDIO_EXTENSIONS:
            return False, f"Unsupported audio file extension '{ext}'. Supported: {SUPPORTED_AUDIO_EXTENSIONS}"

    return True, "Audio file is valid."

class SpeechToTextManager:
    """
    Manages local Whisper model loading, caching, and inference.
    Prefers GPU (CUDA) when available with automatic CPU fallback.
    """

    def __init__(self, model_name: str = "base", device: Optional[str] = None):
        self.model_name = model_name
        self.device = device or ("cuda" if config.stt.device == "cuda" else "cpu")
        self.model = None
        self._load_model()

    def _load_model(self):
        if not WHISPER_AVAILABLE:
            print("[STT WARNING] `openai-whisper` package unavailable. Running in dry-run/mock mode.")
            return

        try:
            print(f"[STT] Loading local model '{self.model_name}' on device '{self.device}'...")
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"[STT] Model '{self.model_name}' loaded successfully on '{self.device}'.")
        except Exception as e:
            print(f"[STT WARNING] GPU initialization failed ({e}). Falling back to CPU...")
            try:
                self.device = "cpu"
                self.model = whisper.load_model(self.model_name, device="cpu")
                print(f"[STT] Model '{self.model_name}' successfully loaded on CPU fallback.")
            except Exception as ex:
                print(f"[STT ERROR] Failed to load model '{self.model_name}': {ex}")
                self.model = None

# Global model manager instance cache
_GLOBAL_STT_MANAGER: Optional[SpeechToTextManager] = None

def get_stt_manager(model_name: str = "base", device: Optional[str] = None) -> SpeechToTextManager:
    """Returns a cached global SpeechToTextManager instance to prevent redundant model reloads."""
    global _GLOBAL_STT_MANAGER
    if _GLOBAL_STT_MANAGER is None or _GLOBAL_STT_MANAGER.model_name != model_name:
        _GLOBAL_STT_MANAGER = SpeechToTextManager(model_name=model_name, device=device)
    return _GLOBAL_STT_MANAGER


def audio_to_transcript(
    audio_file: Union[str, pathlib.Path],
    language: Optional[str] = None,
    model_name: Optional[str] = "base",
    device: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transcribes an audio file into text using local multilingual Whisper model.
    
    Args:
        audio_file: Path to audio file (.wav, .mp3, .m4a, .flac, etc.)
        language: Optional language code ('hi', 'en', 'ta'). If None, auto-detected.
        model_name: Whisper model size ('tiny', 'base', 'small', 'medium', 'large').
        device: 'cuda' or 'cpu'.
        
    Returns:
        Structured dictionary containing transcript, confidence, timing, language flags,
        and success/error status.
    """
    start_time = time.time()
    audio_path = str(audio_file)
    
    # -------------------------------------------------------------------------
    # 1. Validation Checks
    # -------------------------------------------------------------------------
    # File existence check
    if not os.path.exists(audio_path):
        return {
            "success": False,
            "error": f"Audio file not found: {audio_path}",
            "transcript": "",
            "detected_language": "unknown",
            "requested_language": language,
            "model_name": model_name,
            "processing_time": round(time.time() - start_time, 3),
            "confidence_score": 0.0,
            "duration_sec": 0.0,
            "segments": [],
            "tested_status": "INVALID",
            "safety_disclaimer": config.safety.medical_disclaimer
        }

    # Unsupported format check
    ext = os.path.splitext(audio_path)[1].lower()
    if ext not in SUPPORTED_AUDIO_EXTENSIONS:
        return {
            "success": False,
            "error": f"Unsupported audio format '{ext}'. Supported formats: {sorted(list(SUPPORTED_AUDIO_EXTENSIONS))}",
            "transcript": "",
            "detected_language": "unknown",
            "requested_language": language,
            "model_name": model_name,
            "processing_time": round(time.time() - start_time, 3),
            "confidence_score": 0.0,
            "duration_sec": 0.0,
            "segments": [],
            "tested_status": "INVALID",
            "safety_disclaimer": config.safety.medical_disclaimer
        }

    # Empty file check (0 bytes)
    file_size = os.path.getsize(audio_path)
    if file_size == 0:
        return {
            "success": False,
            "error": f"Audio file is empty (0 bytes): {audio_path}",
            "transcript": "",
            "detected_language": "unknown",
            "requested_language": language,
            "model_name": model_name,
            "processing_time": round(time.time() - start_time, 3),
            "confidence_score": 0.0,
            "duration_sec": 0.0,
            "segments": [],
            "tested_status": "INVALID",
            "safety_disclaimer": config.safety.medical_disclaimer
        }

    # Audio data loading & duration calculation
    try:
        import librosa
        audio_input, sr = librosa.load(audio_path, sr=16000)
        duration_sec = float(len(audio_input)) / 16000.0
    except Exception as read_err:
        print(f"[STT WARNING] librosa.load failed for '{audio_path}': {read_err}")
        audio_input = audio_path
        duration_sec = 0.0

    # Excessively long audio check
    if duration_sec > MAX_AUDIO_DURATION_SEC:
        return {
            "success": False,
            "error": f"Audio duration ({duration_sec:.1f}s) exceeds maximum threshold ({MAX_AUDIO_DURATION_SEC}s)",
            "transcript": "",
            "detected_language": "unknown",
            "requested_language": language,
            "model_name": model_name,
            "processing_time": round(time.time() - start_time, 3),
            "confidence_score": 0.0,
            "duration_sec": round(duration_sec, 2),
            "segments": [],
            "tested_status": "INVALID",
            "safety_disclaimer": config.safety.medical_disclaimer
        }

    # -------------------------------------------------------------------------
    # 2. Model Inference Execution
    # -------------------------------------------------------------------------
    manager = get_stt_manager(model_name=model_name, device=device)
    
    if manager.model is None:
        return {
            "success": False,
            "error": "STT model initialization failed.",
            "transcript": "",
            "detected_language": "unknown",
            "requested_language": language,
            "model_name": model_name,
            "processing_time": round(time.time() - start_time, 3),
            "confidence_score": 0.0,
            "duration_sec": round(duration_sec, 2),
            "segments": [],
            "tested_status": "ERROR",
            "safety_disclaimer": config.safety.medical_disclaimer
        }

    options = {
        "fp16": (manager.device == "cuda"),
        "verbose": False
    }
    if language:
        options["language"] = language
        if language == "hi":
            options["initial_prompt"] = "यह हिंदी भाषा का ऑडियो है: मुझे बचाओ, धमकी, डर, मदद, जान से मार"
        elif language == "mr":
            options["initial_prompt"] = "हे मराठी भाषेतील ऑडिओ आहे: मला मदत करा, धमकी, मारहाण, भीती, वाचवा"

    try:
        res = manager.model.transcribe(audio_input, **options)
    except Exception as infer_err:
        return {
            "success": False,
            "error": f"Transcription inference error: {infer_err}",
            "transcript": "",
            "detected_language": "unknown",
            "requested_language": language,
            "model_name": model_name,
            "processing_time": round(time.time() - start_time, 3),
            "confidence_score": 0.0,
            "duration_sec": round(duration_sec, 2),
            "segments": [],
            "tested_status": "ERROR",
            "safety_disclaimer": config.safety.medical_disclaimer
        }

    # -------------------------------------------------------------------------
    # 3. Post-Processing & Metadata Formatting
    # -------------------------------------------------------------------------
    detected_lang = res.get("language", language or "hi")
    
    if detected_lang in TESTED_LANGUAGES:
        tested_status = f"TESTED ({TESTED_LANGUAGES[detected_lang]})"
    elif detected_lang in UNTESTED_LANGUAGES:
        tested_status = f"UNTESTED ({UNTESTED_LANGUAGES[detected_lang]})"
    else:
        tested_status = f"UNTESTED ({detected_lang})"

    transcript_text = res.get("text", "").strip()
    segments_data = []
    logprobs = []

    for idx, seg in enumerate(res.get("segments", [])):
        avg_lp = seg.get("avg_logprob", -0.5)
        logprobs.append(avg_lp)
        seg_conf = float(np.clip(math.exp(avg_lp), 0.0, 1.0))
        
        segments_data.append({
            "id": idx,
            "start": round(float(seg.get("start", 0.0)), 2),
            "end": round(float(seg.get("end", 0.0)), 2),
            "text": seg.get("text", "").strip(),
            "confidence": round(seg_conf, 3),
            "avg_logprob": round(float(avg_lp), 3)
        })

    mean_lp = float(np.mean(logprobs)) if logprobs else -0.5
    overall_conf = round(float(np.clip(math.exp(mean_lp), 0.0, 1.0)), 3)
    processing_time = round(time.time() - start_time, 3)

    return {
        "success": True,
        "error": None,
        "transcript": transcript_text,
        "detected_language": detected_lang,
        "requested_language": language,
        "model_name": f"whisper-{model_name}",
        "processing_time": processing_time,
        "confidence_score": overall_conf,
        "duration_sec": round(duration_sec, 2),
        "segments": segments_data,
        "tested_status": tested_status,
        "safety_disclaimer": config.safety.medical_disclaimer
    }
