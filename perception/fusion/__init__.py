"""
Perception-to-SVI Fusion & Risk Scoring Engine
==============================================================================
Aggregates speech, acoustic features, and text distress outputs into a standardized
SVI score (0-100) and risk tier payload for downstream decision consumption.
==============================================================================
"""

from .svi_engine import (
    calculate_svi,
    compute_perception_fusion,
    PerceptionFusionEngine
)
from .schemas import SVIResult, PerceptionPayload

__all__ = [
    "calculate_svi",
    "compute_perception_fusion",
    "PerceptionFusionEngine",
    "SVIResult",
    "PerceptionPayload"
]
