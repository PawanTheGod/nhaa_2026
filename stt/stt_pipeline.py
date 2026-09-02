"""
Multilingual Speech-to-Text (STT) Pipeline
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
SAFETY & ETHICAL NOTICE:
- Perception signal generator for helpline AI triage.
- NOT A CLINICAL OR MEDICAL DIAGNOSIS.
- Transcripts and metadata are provided for human-in-the-loop triage prioritization.
==============================================================================
"""

import os
import math
import time

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import numpy as np

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

from config import config, TESTED_LANGUAGES, UNTESTED_LANGUAGES
from utils.audio_utils import get_audio_duration

@dataclass
class STTSegment:
    """Represents a timed segment within the audio transcript."""
    id: int
    start: float
    end: float
    text: str
    confidence: float
    avg_logprob: float

@dataclass
class STTResult:
    """Structured perception output of the Speech-To-Text pipeline."""
    transcript: str
    language: str
    language_confidence: float
    duration_sec: float
    segments: List[Dict[str, Any]]
    tested_status: str  # "TESTED" for en/hi/ta, "UNTESTED" for others
    confidence_score: float
    safety_disclaimer: str = field(default=config.safety.medical_disclaimer)
    model_name: str = field(default="whisper-base")
    processed_timestamp: float = field(default_factory=time.time)

    def to_mongo_dict(self) -> Dict[str, Any]:
        """Returns MongoDB-compatible document format."""
        return {
            "transcript": self.transcript,
            "language": self.language,
            "language_confidence": self.language_confidence,
            "duration_sec": self.duration_sec,
            "segments": self.segments,
            "tested_status": self.tested_status,
            "confidence_score": self.confidence_score,
            "safety_disclaimer": self.safety_disclaimer,
            "model_name": self.model_name,
            "processed_timestamp": self.processed_timestamp,
        }

class SpeechToTextPipeline:
    """
    Open-source Speech-To-Text Pipeline using OpenAI Whisper.
    Supports Hindi ('hi'), English ('en'), Tamil ('ta'), and other Indic languages.
    """

    def __init__(
        self,
        model_size: Optional[str] = None,
        device: Optional[str] = None
    ):
        """
        Initializes the STT model.
        
        Args:
            model_size: 'tiny', 'base', 'small', 'medium', or 'large'.
            device: 'cuda' or 'cpu'.
        """
        self.model_size = model_size or config.stt.model_size
        self.device = device or config.stt.device
        self.model = None
        
        if not WHISPER_AVAILABLE:
            print("[STT WARNING] `openai-whisper` package is not available. STT running in mock mode.")
            return

        try:
            print(f"[STT] Loading Whisper model '{self.model_size}' on device '{self.device}'...")
            self.model = whisper.load_model(self.model_size, device=self.device)
            print(f"[STT] Whisper '{self.model_size}' successfully loaded.")
        except Exception as e:
            print(f"[STT WARNING] Could not load model on '{self.device}' ({e}). Falling back to CPU...")
            try:
                self.device = "cpu"
                self.model = whisper.load_model(self.model_size, device="cpu")
                print(f"[STT] Whisper '{self.model_size}' loaded on CPU fallback.")
            except Exception as ex:
                print(f"[STT ERROR] Failed to load Whisper model: {ex}")
                self.model = None

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> STTResult:
        """
        Transcribes an audio file into text with timing and confidence metadata.
        
        Args:
            audio_path: Path to the input audio file (.wav, .mp3, .flac).
            language: Optional language code ('hi', 'en', 'ta'). If None, auto-detected.
            task: 'transcribe' (speech-to-text in original language) or 'translate' (to English).
            
        Returns:
            STTResult object containing transcript, timings, confidence, and language status.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        duration = get_audio_duration(audio_path) if audio_path.endswith(".wav") else 0.0

        # Validate language testing status
        lang_code = language.lower() if language else "hi"
        if lang_code in TESTED_LANGUAGES:
            tested_status = f"TESTED ({TESTED_LANGUAGES[lang_code]})"
        elif lang_code in UNTESTED_LANGUAGES:
            tested_status = f"UNTESTED ({UNTESTED_LANGUAGES[lang_code]})"
        else:
            tested_status = f"UNTESTED ({lang_code})"

        # If model is unavailable, return structured fallback / mock result
        if self.model is None:
            return STTResult(
                transcript="[STT Fallback] Audio processed. Model unavailable.",
                language=lang_code,
                language_confidence=0.50,
                duration_sec=duration,
                segments=[],
                tested_status=tested_status,
                confidence_score=0.50,
                model_name=f"whisper-{self.model_size}-mock"
            )

        # Read audio into numpy array to bypass ffmpeg dependency on Windows
        try:
            from scipy.io import wavfile
            sr, raw_data = wavfile.read(audio_path)
            # Handle stereo to mono conversion
            if len(raw_data.shape) > 1:
                raw_data = raw_data.mean(axis=1)
            # Normalize int16 or int32 PCM to float32 [-1.0, 1.0]
            if raw_data.dtype == np.int16:
                audio_input = raw_data.astype(np.float32) / 32768.0
            elif raw_data.dtype == np.int32:
                audio_input = raw_data.astype(np.float32) / 2147483648.0
            elif raw_data.dtype == np.float32:
                audio_input = raw_data
            else:
                audio_input = raw_data.astype(np.float32)
        except Exception as load_err:
            print(f"[STT WARNING] Custom wav read failed ({load_err}), attempting direct file path pass...")
            audio_input = audio_path

        # Execute transcription with Whisper
        options = {
            "task": task,
            "fp16": (self.device == "cuda"),
            "verbose": False
        }
        if language:
            options["language"] = language

        result = self.model.transcribe(audio_input, **options)

        detected_language = result.get("language", lang_code)
        
        # Check validation status of detected language
        if detected_language in TESTED_LANGUAGES:
            tested_status = f"TESTED ({TESTED_LANGUAGES[detected_language]})"
        elif detected_language in UNTESTED_LANGUAGES:
            tested_status = f"UNTESTED ({UNTESTED_LANGUAGES[detected_language]})"
        else:
            tested_status = f"UNTESTED ({detected_language})"

        transcript_text = result.get("text", "").strip()

        # Parse segments and compute segment confidence from avg_logprob
        segments_data = []
        logprobs = []
        
        for idx, seg in enumerate(result.get("segments", [])):
            avg_logprob = seg.get("avg_logprob", -0.5)
            logprobs.append(avg_logprob)
            # Map logprob [-2.0, 0.0] roughly to confidence [0.0, 1.0]
            seg_conf = float(np.clip(math.exp(avg_logprob), 0.0, 1.0))
            
            segments_data.append({
                "id": idx,
                "start": round(float(seg.get("start", 0.0)), 2),
                "end": round(float(seg.get("end", 0.0)), 2),
                "text": seg.get("text", "").strip(),
                "confidence": round(seg_conf, 3),
                "avg_logprob": round(float(avg_logprob), 3)
            })

        mean_logprob = float(np.mean(logprobs)) if logprobs else -0.5
        overall_confidence = round(float(np.clip(math.exp(mean_logprob), 0.0, 1.0)), 3)

        return STTResult(
            transcript=transcript_text,
            language=detected_language,
            language_confidence=0.95 if language else 0.85,
            duration_sec=round(duration, 2),
            segments=segments_data,
            tested_status=tested_status,
            confidence_score=overall_confidence,
            model_name=f"whisper-{self.model_size}"
        )
