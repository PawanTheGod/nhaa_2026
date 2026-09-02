"""
Analytics & Dashboard Subpackage for AI Perception Layer
==============================================================================
Provides historical SVI score trends, risk tier distributions, flag frequency
metrics, and channel/language volume aggregations.
==============================================================================
"""

from .schemas import (
    SVITrendItem,
    SVITrendResponse,
    RiskDistributionItem,
    RiskDistributionResponse,
    FlagFrequencyItem,
    FlagFrequencyResponse,
    ChannelLanguageVolumeItem,
    ChannelLanguageVolumeResponse
)
from .repository import (
    AnalyticsRepository,
    MockAnalyticsRepository,
    get_analytics_repository
)

__all__ = [
    "SVITrendItem",
    "SVITrendResponse",
    "RiskDistributionItem",
    "RiskDistributionResponse",
    "FlagFrequencyItem",
    "FlagFrequencyResponse",
    "ChannelLanguageVolumeItem",
    "ChannelLanguageVolumeResponse",
    "AnalyticsRepository",
    "MockAnalyticsRepository",
    "get_analytics_repository"
]
