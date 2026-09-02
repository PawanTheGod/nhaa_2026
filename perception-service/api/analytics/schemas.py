"""
Pydantic Response Schemas for Perception Analytics & Dashboard Endpoints
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SVITrendItem(BaseModel):
    """Aggregate SVI trend item per time period / location."""
    time_period: str = Field(..., description="Date or week identifier (e.g. '2026-W35' or '2026-09-01')")
    district: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)
    average_svi: float = Field(..., ge=0.0, le=100.0, description="Average SVI score in period")
    case_count: int = Field(..., ge=0, description="Total case count in period")


class SVITrendResponse(BaseModel):
    """SVI trend time-series response."""
    period_type: str = Field(default="weekly", description="'weekly' or 'daily'")
    total_cases_analyzed: int = Field(..., ge=0)
    trends: List[SVITrendItem] = Field(default_factory=list)


class RiskDistributionItem(BaseModel):
    """Risk tier count and percentage distribution."""
    risk_tier: str = Field(..., description="'Low', 'Moderate', 'High', or 'Critical'")
    count: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0.0, le=100.0)


class RiskDistributionResponse(BaseModel):
    """Risk tier distribution response."""
    total_cases: int = Field(..., ge=0)
    distribution: List[RiskDistributionItem] = Field(default_factory=list)


class FlagFrequencyItem(BaseModel):
    """Frequency count for a specific risk flag category."""
    flag_name: str = Field(..., description="Risk indicator flag identifier")
    count: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0.0, le=100.0)


class FlagFrequencyResponse(BaseModel):
    """Flag frequency breakdown response."""
    total_flags_count: int = Field(..., ge=0)
    flags: List[FlagFrequencyItem] = Field(default_factory=list)


class ChannelLanguageVolumeItem(BaseModel):
    """Case volume breakdown item by channel and language."""
    channel: str = Field(..., description="'ivrs', 'phone', 'chat', 'portal', 'mobile_app'")
    language: str = Field(..., description="'hi', 'en', 'ta'")
    count: int = Field(..., ge=0)


class ChannelLanguageVolumeResponse(BaseModel):
    """Channel and language case volume breakdown response."""
    total_cases: int = Field(..., ge=0)
    volumes: List[ChannelLanguageVolumeItem] = Field(default_factory=list)
