"""
Multilingual Text Distress-Classification Package
==============================================================================
Analyzes citizen text / transcripts for distress risk indicators (trauma, fear,
depression, suicidal ideation, intimidation, isolation, extreme vulnerability).
==============================================================================
"""

from .text_classifier import text_to_distress_flags, MultilingualTextDistressClassifier, get_text_classifier
from .schemas import DistressFlag, TextDistressResponse

__all__ = [
    "text_to_distress_flags",
    "MultilingualTextDistressClassifier",
    "get_text_classifier",
    "DistressFlag",
    "TextDistressResponse"
]
