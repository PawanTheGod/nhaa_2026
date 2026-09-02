"""
NHAA 14566 / SIH 26093 - AI Perception Layer Configuration
==============================================================================
SAFETY & ETHICAL NOTICE:
- This module provides perception-level risk indicators for AI triage assistance.
- IT DOES NOT PROVIDE CLINICAL OR MEDICAL DIAGNOSES.
- Signals generated (STT, emotion, distress) are passed to downstream decision
  layers and human officers. NO AUTONOMOUS EMERGENCY DISPATCH IS PERFORMED.
==============================================================================
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict

# Supported Proof-of-Concept Languages & Validation Status
TESTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
}

UNTESTED_LANGUAGES = {
    "bn": "Bengali",
    "te": "Telugu",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
}

# Formal Language Model Capability Matrix
# Status Categories: SUPPORTED, TESTED, EXPERIMENTAL, UNSUPPORTED
LANGUAGE_CAPABILITY_MATRIX = {
    "en": {
        "language_name": "English",
        "stt": "SUPPORTED",
        "acoustic": "SUPPORTED",
        "ser": "SUPPORTED",
        "text": "SUPPORTED",
        "combined_svi": "SUPPORTED",
        "tested": "TESTED (English)"
    },
    "hi": {
        "language_name": "Hindi",
        "stt": "SUPPORTED",
        "acoustic": "SUPPORTED",
        "ser": "EXPERIMENTAL",
        "text": "SUPPORTED",
        "combined_svi": "SUPPORTED",
        "tested": "TESTED (Hindi)"
    },
    "mr": {
        "language_name": "Marathi",
        "stt": "SUPPORTED",
        "acoustic": "SUPPORTED",
        "ser": "EXPERIMENTAL",
        "text": "SUPPORTED",
        "combined_svi": "SUPPORTED",
        "tested": "TESTED (Marathi)"
    },
    "ta": {
        "language_name": "Tamil",
        "stt": "SUPPORTED",
        "acoustic": "SUPPORTED",
        "ser": "EXPERIMENTAL",
        "text": "SUPPORTED",
        "combined_svi": "SUPPORTED",
        "tested": "TESTED (Tamil)"
    }
}

@dataclass
class STTConfig:
    """Speech-to-Text Pipeline Configuration."""
    model_size: str = os.getenv("WHISPER_MODEL_SIZE", "base")  # 'tiny', 'base', 'small', 'medium', 'large'
    device: str = os.getenv("STT_DEVICE", "cuda" if os.getenv("USE_CUDA", "1") == "1" else "cpu")
    compute_type: str = "float16"  # float16 for CUDA, float32 for CPU
    default_language: str = "hi"
    sample_rate: int = 16000

@dataclass
class SVIConfig:
    """Configurable Stress Vulnerability Index (SVI) thresholds & weights."""
    schema_version: str = "1.0"
    
    # Configurable Risk Tier Thresholds (0-100)
    tier_low_max: int = 24       # 0 - 24
    tier_moderate_max: int = 49  # 25 - 49
    tier_high_max: int = 74      # 50 - 74
    tier_critical_min: int = 75  # 75 - 100

    # Max score cap
    max_svi_score: int = 100
    min_svi_score: int = 0

    # Flag severity weights for text distress categories (0-100 scale)
    flag_weights: Dict[str, float] = field(default_factory=lambda: {
        "suicidal_ideation": 85.0,
        "intimidation": 75.0,
        "trauma": 55.0,
        "fear": 45.0,
        "extreme_vulnerability": 45.0,
        "depression": 35.0,
        "isolation": 25.0
    })

    # Speech emotion weights
    emotion_weights: Dict[str, float] = field(default_factory=lambda: {
        "fear": 30.0,
        "fearful": 30.0,
        "angry": 25.0,
        "sad": 20.0,
        "surprised": 10.0,
        "neutral": 0.0,
        "happy": 0.0
    })

@dataclass
class SafetyConfig:
    """Safety and Privacy Settings."""
    medical_disclaimer: str = (
        "PERCEPTION SIGNAL ONLY: Not a medical or clinical diagnosis. "
        "Intended solely for helpline triage prioritization under human oversight."
    )
    store_raw_audio: bool = False  # Privacy: avoid storing raw audio by default
    store_transcripts: bool = True
    anonymize_pii: bool = True

@dataclass
class MongoConfig:
    """MongoDB Schema & Compatibility Settings."""
    uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    database_name: str = os.getenv("MONGODB_DB", "nhaa_triage")
    collection_transcripts: str = "stt_transcripts"
    collection_perceptions: str = "perception_results"

@dataclass
class AppConfig:
    """Master Perception Layer Configuration."""
    stt: STTConfig = field(default_factory=STTConfig)
    svi: SVIConfig = field(default_factory=SVIConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    mongo: MongoConfig = field(default_factory=MongoConfig)

config = AppConfig()
