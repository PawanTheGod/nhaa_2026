"""
Acoustic Speech-Feature Extraction Package
==============================================================================
Extracts interpretable acoustic features (pitch F0 statistics, pause patterns,
energy dynamics, zero crossing rate, speaking rate proxy) for AI Helpline triage.
==============================================================================
"""

from .feature_extractor import extract_acoustic_features, AcousticFeatureExtractor

__all__ = ["extract_acoustic_features", "AcousticFeatureExtractor"]
