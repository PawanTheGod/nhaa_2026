"""
Pydantic Schemas for Explainability & Perception Evidence Layer
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
"""

from typing import List
from pydantic import BaseModel, Field

from perception.schemas.perception_contract import (
    RawMeasurement,
    ModelPrediction,
    FlagEvidence
)

class UnifiedEvidenceReport(BaseModel):
    """Complete perception evidence report merging speech and text perception channels."""
    model_config = {"protected_namespaces": ()}

    flags: List[FlagEvidence] = Field(default_factory=list)
    raw_measurements: List[RawMeasurement] = Field(default_factory=list)
    model_predictions: List[ModelPrediction] = Field(default_factory=list)
    safety_disclaimer: str = Field(...)

__all__ = [
    "RawMeasurement",
    "ModelPrediction",
    "FlagEvidence",
    "UnifiedEvidenceReport"
]
