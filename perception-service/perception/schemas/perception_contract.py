"""
Formal Versioned Output Contract Schema for AI Perception Layer
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Target Consumers:
- Aatmman's Agentic Decision Layer (Downstream policy & escalation engine)
- Vinit's Central Case API / Backend (Upstream case management & persistence)
==============================================================================
"""

import time
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator

SCHEMA_VERSION = "1.0"
VALID_RISK_TIERS = {"low", "moderate", "high", "critical", "Low", "Moderate", "High", "Critical"}
VALID_CHANNELS = {"ivrs", "phone", "chat", "chatbot", "portal", "mobile_app"}
VALID_MODALITIES = {"audio", "text"}

ALLOWED_FLAG_NAMES = {
    "trauma",
    "fear",
    "depression",
    "suicidal_ideation",
    "intimidation",
    "isolation",
    "extreme_vulnerability"
}


class LanguageMetadata(BaseModel):
    """Language detection, capabilities, and validation status."""
    code: str = Field(..., description="ISO 639-1 language code (e.g. 'en', 'hi', 'mr', 'ta')")
    name: Optional[str] = Field(default=None, description="Language display name e.g. 'Marathi'")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="Language detection confidence score")
    stt_status: str = Field(default="SUPPORTED", description="STT support status: 'SUPPORTED', 'TESTED', 'EXPERIMENTAL'")
    ser_status: str = Field(default="EXPERIMENTAL", description="SER support status: 'SUPPORTED' or 'EXPERIMENTAL'")
    text_status: str = Field(default="SUPPORTED", description="Text support status: 'SUPPORTED' or 'EXPERIMENTAL'")
    tested_status: str = Field(..., description="Validation status: 'TESTED (Language)' or 'UNTESTED'")


class SVIResult(BaseModel):
    """Stress Vulnerability Index (SVI) score and risk tier."""
    score: int = Field(..., ge=0, le=100, description="Composite SVI score between 0 and 100")
    risk_tier: str = Field(..., description="Risk tier: 'Low', 'Moderate', 'High', or 'Critical'")

    @field_validator("risk_tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        clean_tier = v.lower().strip()
        canonical_map = {
            "low": "Low",
            "moderate": "Moderate",
            "high": "High",
            "critical": "Critical"
        }
        if clean_tier not in canonical_map:
            raise ValueError(f"Risk tier '{v}' must be one of {sorted(list(canonical_map.keys()))}")
        return canonical_map[clean_tier]


class FlagEvidence(BaseModel):
    """Unified risk flag containing concise, auditable evidence and source provenance."""
    name: str = Field(..., description="Risk indicator category identifier")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    signals: List[str] = Field(..., min_length=1, description="Concise explainable signal strings")
    source: List[str] = Field(..., min_length=1, description="Contributing modalities e.g. ['audio', 'text']")

    @field_validator("name")
    @classmethod
    def validate_flag_name(cls, v: str) -> str:
        clean_name = v.lower().strip()
        if clean_name not in ALLOWED_FLAG_NAMES:
            mapping = {
                "trauma indicators": "trauma",
                "depression-related language": "depression",
                "suicidal ideation": "suicidal_ideation",
                "social isolation": "isolation"
            }
            if clean_name in mapping:
                return mapping[clean_name]
            raise ValueError(f"Flag name '{v}' must be one of {sorted(list(ALLOWED_FLAG_NAMES))}")
        return clean_name

    @field_validator("source")
    @classmethod
    def validate_sources(cls, v: List[str]) -> List[str]:
        for s in v:
            if s not in VALID_MODALITIES:
                raise ValueError(f"Source modality '{s}' must be one of {VALID_MODALITIES}")
        return sorted(list(set(v)))


class RawMeasurement(BaseModel):
    """Grounded physical audio or text measurement."""
    source: str = Field(..., description="Modality source: 'audio' or 'text'")
    type: str = Field(..., description="Measurement category e.g. 'acoustic_feature', 'text_pattern'")
    name: str = Field(..., description="Measurement identifier key e.g. 'pause_duration', 'pitch_std'")
    value: Union[float, int, str] = Field(..., description="Grounded numeric or string value")
    unit: str = Field(..., description="Unit of measurement e.g. 'seconds', 'Hz', 'RMS', 'matches'")

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        if v not in VALID_MODALITIES:
            raise ValueError(f"RawMeasurement source '{v}' must be one of {VALID_MODALITIES}")
        return v


class ModelPrediction(BaseModel):
    """Direct probability prediction from a perception model."""
    model_config = {"protected_namespaces": ()}

    source: str = Field(..., description="Modality source: 'audio' or 'text'")
    type: str = Field(default="model_prediction")
    name: str = Field(..., description="Target predicted label e.g. 'fear', 'intimidation'")
    confidence: float = Field(..., ge=0.0, le=1.0)
    model_name: str = Field(..., description="Model identifier checkpoint name")

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        if v not in VALID_MODALITIES:
            raise ValueError(f"ModelPrediction source '{v}' must be one of {VALID_MODALITIES}")
        return v


class SourcesMap(BaseModel):
    """Active perception data channels."""
    speech: bool = Field(..., description="True if audio speech channel was processed")
    text: bool = Field(..., description="True if text transcript/chat channel was processed")


class ModelMetadataMap(BaseModel):
    """Metadata detailing models used across perception layers."""
    model_config = {"protected_namespaces": ()}

    stt_model: Optional[str] = Field(default=None, description="STT model name e.g. 'whisper-tiny'")
    ser_model: Optional[str] = Field(default=None, description="SER model checkpoint e.g. 'wav2vec2-lg-xlsr'")
    text_model: Optional[str] = Field(default=None, description="Text model checkpoint e.g. 'google/muril-base-cased'")
    execution_time_sec: float = Field(..., ge=0.0, description="Total perception processing time in seconds")


class PerceptionOutputContract(BaseModel):
    """
    Formal Versioned Output Contract for AI Perception Layer (v1.0).
    Shared schema consumed directly by Aatmman's Decision Layer & Vinit's Case API.
    """
    model_config = {"protected_namespaces": ()}

    schema_version: str = Field(default=SCHEMA_VERSION, description="Contract schema version")
    case_id: Optional[str] = Field(default=None, description="Unique Central Case API Case ID")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of perception execution")
    channel: str = Field(default="ivrs", description="Ingestion channel: 'ivrs', 'phone', 'chat', 'chatbot', 'portal', 'mobile_app'")
    language: LanguageMetadata = Field(
        default_factory=lambda: LanguageMetadata(code="hi", confidence=0.95, tested_status="TESTED (Hindi)"),
        description="Language code and testing status"
    )
    svi: SVIResult = Field(..., description="Stress Vulnerability Index score and risk tier")
    stt_transcript: Optional[str] = Field(default=None, description="Automatically transcribed speech-to-text transcript from audio")
    flags: List[FlagEvidence] = Field(default_factory=list, description="List of extracted risk flag evidence")
    sources: SourcesMap = Field(..., description="Active source modalities processed")
    raw_measurements: List[RawMeasurement] = Field(default_factory=list, description="Grounded physical measurements")
    model_predictions: List[ModelPrediction] = Field(default_factory=list, description="Direct neural model likelihoods")
    model_metadata: ModelMetadataMap = Field(..., description="Perception models metadata")
    safety_disclaimer: str = Field(..., description="Mandatory non-clinical disclaimer")

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v: str) -> str:
        clean_ch = v.lower().strip()
        if clean_ch not in VALID_CHANNELS:
            raise ValueError(f"Channel '{v}' must be one of {VALID_CHANNELS}")
        return clean_ch

    def to_vinit_payload(self, case_id_override: Optional[int] = None) -> Dict[str, Any]:
        """
        Formats perception contract into Vinit's Central Case API RiskAssessmentCreate payload format.
        Matching schema: RiskAssessmentCreate(case_id, svi_score, risk_tier, flags, explanation_text, model_version)
        """
        # Parse numeric case_id
        parsed_case_id = case_id_override
        if parsed_case_id is None and self.case_id:
            try:
                # Extract numeric digits if string like "CASE-100"
                import re
                nums = re.findall(r'\d+', str(self.case_id))
                parsed_case_id = int(nums[-1]) if nums else 1
            except Exception:
                parsed_case_id = 1
        elif parsed_case_id is None:
            parsed_case_id = 1

        # Format flags as dict {flag_name: confidence}
        flags_dict = {f.name: f.confidence for f in self.flags}
        
        # Build explanation text summary
        signals_summary = []
        for f in self.flags:
            signals_summary.extend(f.signals)
        explanation = f"SVI {self.svi.score} ({self.svi.risk_tier}). Signals: {'; '.join(signals_summary[:3])}" if signals_summary else f"SVI {self.svi.score} ({self.svi.risk_tier})."

        return {
            "case_id": parsed_case_id,
            "svi_score": float(self.svi.score),
            "risk_tier": self.svi.risk_tier.lower(),
            "flags": flags_dict,
            "explanation_text": explanation,
            "model_version": self.schema_version
        }
