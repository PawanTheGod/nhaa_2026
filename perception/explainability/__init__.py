"""
Explainability & Evidence Generation Package
==============================================================================
Provides grounded, auditable perception evidence maps preserving raw measurements,
neural model predictions, and merged risk flag provenance.
==============================================================================
"""

from .evidence_builder import (
    speech_to_evidence,
    text_to_evidence,
    merge_evidence,
    build_unified_evidence_report
)
from .schemas import (
    RawMeasurement,
    ModelPrediction,
    FlagEvidence,
    UnifiedEvidenceReport
)

__all__ = [
    "speech_to_evidence",
    "text_to_evidence",
    "merge_evidence",
    "build_unified_evidence_report",
    "RawMeasurement",
    "ModelPrediction",
    "FlagEvidence",
    "UnifiedEvidenceReport"
]
