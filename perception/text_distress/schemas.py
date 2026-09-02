"""
Pydantic Schemas for Multilingual Text Distress Classification
==============================================================================
Validates structured perception outputs, confidence bounds, and signal lists.
==============================================================================
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

ALLOWED_FLAG_NAMES = {
    "trauma",
    "fear",
    "depression",
    "suicidal_ideation",
    "intimidation",
    "isolation",
    "extreme_vulnerability"
}

class DistressFlag(BaseModel):
    """Pydantic model representing an extracted distress risk flag."""
    name: str = Field(..., description="Name of the risk indicator category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    signals: List[str] = Field(default_factory=list, description="List of raw evidence signal strings")

    @field_validator("name")
    @classmethod
    def validate_flag_name(cls, v: str) -> str:
        clean_v = v.lower().strip()
        if clean_v not in ALLOWED_FLAG_NAMES:
            # Map canonical variants
            mapping = {
                "trauma indicators": "trauma",
                "depression-related language": "depression",
                "suicidal ideation": "suicidal_ideation",
                "suicidal_ideation_indicators": "suicidal_ideation",
                "social isolation": "isolation",
                "social_isolation": "isolation"
            }
            if clean_v in mapping:
                return mapping[clean_v]
            raise ValueError(f"Flag name '{v}' must be one of {sorted(list(ALLOWED_FLAG_NAMES))}")
        return clean_v


class TextDistressResponse(BaseModel):
    """Pydantic model for complete text distress classification response."""
    success: bool = Field(default=True)
    error: Optional[str] = Field(default=None)
    language: str = Field(..., description="Detected or specified ISO language code")
    tested_status: str = Field(..., description="Validation status: TESTED or UNTESTED")
    flags: List[DistressFlag] = Field(default_factory=list)
    model: str = Field(..., description="Name of model used (e.g. google/muril-base-cased)")
    method: str = Field(..., description="Classification path: 'fine_tuned' or 'fallback'")
    processing_time: float = Field(..., ge=0.0)
    safety_disclaimer: str = Field(...)
