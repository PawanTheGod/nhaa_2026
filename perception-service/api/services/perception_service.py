"""
Perception Service Engine for FastAPI Endpoint Handlers
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Encapsulates ML model loading, temporary audio file lifecycle management,
and execution of the multi-channel perception pipeline.
==============================================================================
"""

import os
import sys
import tempfile
import time
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from config import config, TESTED_LANGUAGES, LANGUAGE_CAPABILITY_MATRIX
from perception.stt import SpeechToTextManager, audio_to_transcript
from perception.ser import SpeechEmotionRecognizer, audio_to_emotion
from perception.speech_features import extract_acoustic_features
from perception.text_distress import get_text_classifier, text_to_distress_flags
from perception.fusion import PerceptionFusionEngine
from perception.schemas import (
    PerceptionOutputContract,
    LanguageMetadata,
    SVIResult,
    FlagEvidence,
    RawMeasurement,
    ModelPrediction,
    SourcesMap,
    ModelMetadataMap
)

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB max file size limit


class PerceptionService:
    """
    Singleton Perception Service holding preloaded ML models.
    Models are loaded once during app startup.
    """

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.stt_manager = None
        self.ser_recognizer = None
        self.text_classifier = None
        self.fusion_engine = None
        self.models_loaded = False

    def load_models(self):
        """Loads models ONCE at application startup."""
        print(f"[PerceptionService] Pre-loading ML models on device: '{self.device}'...")
        start_t = time.time()

        # 1. STT Manager (Whisper base model for Indic Devanagari script transcription)
        self.stt_manager = SpeechToTextManager(model_name="base", device=self.device)
        
        # 2. SER Recognizer (Use mock mode in local test/dev if offline to avoid slow downloads)
        ser_model_name = os.getenv("SER_MODEL_NAME", "mock")
        self.ser_recognizer = SpeechEmotionRecognizer(model_name=ser_model_name, device=self.device)

        # 3. Text Distress Classifier
        self.text_classifier = get_text_classifier(model_name="google/muril-base-cased")

        # 4. Fusion Engine
        self.fusion_engine = PerceptionFusionEngine()

        self.models_loaded = True
        
        # 5. Model Warm-up Pass (Eliminates CUDA cold-start latency spike on first user request)
        try:
            print("[PerceptionService] Executing CUDA & model warm-up pass...")
            dummy_text = "मदत करा, धमकी दिली आहे"
            self.text_classifier.classify(dummy_text, language="mr")
            dummy_audio = np.zeros(8000, dtype=np.float32)
            if hasattr(self.ser_recognizer, "predict"):
                self.ser_recognizer.predict(dummy_audio)
            print("[PerceptionService] Model warm-up pass completed cleanly.")
        except Exception as warm_err:
            print(f"[PerceptionService WARNING] Model warm-up skipped: {warm_err}")

        print(f"[PerceptionService] All ML models successfully pre-loaded & warmed up in {time.time() - start_t:.2f}s!")

    def get_model_status(self) -> Dict[str, Any]:
        """Returns current model status for GET /api/v1/perception/models."""
        return {
            "status": "online" if self.models_loaded else "loading",
            "device": self.device,
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
            "vram_allocated_mb": round(torch.cuda.memory_allocated(0) / (1024 * 1024), 2) if torch.cuda.is_available() else 0.0,
            "models": {
                "stt": {"name": "whisper-tiny", "loaded": self.stt_manager is not None},
                "ser": {"name": getattr(self.ser_recognizer, "model_name", "mock"), "loaded": self.ser_recognizer is not None},
                "text": {"name": "google/muril-base-cased", "loaded": self.text_classifier is not None}
            }
        }

    def analyze(
        self,
        audio_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        text: Optional[str] = None,
        language: str = "hi",
        case_id: Optional[str] = None,
        channel: str = "ivrs"
    ) -> PerceptionOutputContract:
        """
        Executes complete multi-channel perception pipeline.
        """
        if not self.models_loaded:
            self.load_models()

        start_time = time.time()
        temp_audio_path = None

        stt_res = None
        ser_res = None
        ac_res = None
        text_res = None

        try:
            # 1. Process Audio Stream (if provided)
            if audio_bytes and len(audio_bytes) > 0:
                ext = Path(filename).suffix.lower() if filename else ".wav"
                if ext not in ALLOWED_AUDIO_EXTENSIONS:
                    ext = ".wav"

                # Create temporary file safely
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                    tmp.write(audio_bytes)
                    temp_audio_path = tmp.name

                # Execute Audio Perception Pipeline (using 'base' model for accurate Devanagari script STT)
                stt_res = audio_to_transcript(temp_audio_path, language=language, model_name="base", device=self.device)
                ser_res = audio_to_emotion(temp_audio_path, model_name=os.getenv("SER_MODEL_NAME", "mock"), device=self.device)
                ac_res = extract_acoustic_features(temp_audio_path)

                # If caller text was not explicitly passed, use STT transcript automatically from audio!
                if (not text or not text.strip()) and stt_res and stt_res.get("success", False) and stt_res.get("transcript"):
                    text = stt_res.get("transcript")
                    print("[PerceptionService] Automatically extracted STT transcript from audio input.")

            # 2. Process Text Stream (if provided or transcribed)
            if text and text.strip():
                text_res_obj = self.text_classifier.classify(text, language=language)
                text_res = text_res_obj.model_dump()

            # 3. Multimodal Fusion & SVI Score Aggregation
            fusion_payload = self.fusion_engine.process_case(
                stt_result=stt_res,
                ser_result=ser_res,
                speech_features_result=ac_res,
                text_distress_result=text_res,
                case_id=case_id
            )

            # Build Detailed Language Metadata & Capabilities
            lang_code = language or (stt_res.get("detected_language") if stt_res else "hi")
            lang_info = LANGUAGE_CAPABILITY_MATRIX.get(lang_code, {
                "language_name": lang_code.upper(),
                "stt": "SUPPORTED" if lang_code in ["en", "hi", "mr", "ta"] else "EXPERIMENTAL",
                "ser": "SUPPORTED" if lang_code == "en" else "EXPERIMENTAL",
                "text": "SUPPORTED" if lang_code in ["en", "hi", "mr", "ta"] else "EXPERIMENTAL",
                "tested": f"UNTESTED ({lang_code})"
            })

            lang_meta = LanguageMetadata(
                code=lang_code,
                name=lang_info.get("language_name"),
                confidence=float(stt_res.get("confidence_score", 0.95)) if stt_res else 0.95,
                stt_status=lang_info.get("stt", "SUPPORTED"),
                ser_status=lang_info.get("ser", "EXPERIMENTAL"),
                text_status=lang_info.get("text", "SUPPORTED"),
                tested_status=lang_info.get("tested", f"TESTED ({TESTED_LANGUAGES.get(lang_code, lang_code)})")
            )

            fusion_payload.language = lang_meta
            fusion_payload.channel = channel.lower().strip()

            return fusion_payload

        finally:
            # Clean up temporary audio file safely
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                except Exception as e:
                    print(f"[PerceptionService WARNING] Could not remove temp audio file '{temp_audio_path}': {e}")
