"""
FastAPI Analytics & Admin Dashboard Route Handlers
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Exposes high-performance aggregation endpoints for SVI trends, risk distributions,
flag frequencies, and channel/language case volume breakdowns.
==============================================================================
"""

from typing import Optional
from fastapi import APIRouter, Query, status

from api.analytics.schemas import (
    SVITrendResponse,
    RiskDistributionResponse,
    FlagFrequencyResponse,
    ChannelLanguageVolumeResponse
)
from api.analytics.repository import get_analytics_repository

router = APIRouter(prefix="/api/v1/perception/analytics", tags=["Perception Dashboard Analytics"])


@router.get(
    "/svi-trend",
    response_model=SVITrendResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Historical SVI Score Trends Over Time",
    description="Returns average SVI scores and case counts grouped weekly or daily with optional district, state, channel, and risk tier filters."
)
async def get_svi_trend(
    district: Optional[str] = Query(None, description="Filter by district name e.g. 'Central Delhi'"),
    state: Optional[str] = Query(None, description="Filter by state name e.g. 'Delhi'"),
    start_date: Optional[str] = Query(None, description="Start date ISO format e.g. '2026-08-01'"),
    end_date: Optional[str] = Query(None, description="End date ISO format e.g. '2026-08-31'"),
    risk_tier: Optional[str] = Query(None, description="Filter by risk tier ('low', 'moderate', 'high', 'critical')"),
    language: Optional[str] = Query(None, description="Filter by ISO language code ('hi', 'en', 'ta')"),
    channel: Optional[str] = Query(None, description="Filter by channel ('ivrs', 'phone', 'chat', 'portal', 'mobile_app')"),
    period: str = Query("weekly", description="Aggregation grouping period ('weekly' or 'daily')")
) -> SVITrendResponse:
    repo = get_analytics_repository()
    return repo.get_svi_trend(
        district=district,
        state=state,
        start_date=start_date,
        end_date=end_date,
        risk_tier=risk_tier,
        language=language,
        channel=channel,
        period=period
    )


@router.get(
    "/risk-distribution",
    response_model=RiskDistributionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Risk Tier Distribution Breakdown",
    description="Returns total counts and percentage distribution across Low, Moderate, High, and Critical risk tiers."
)
async def get_risk_distribution(
    district: Optional[str] = Query(None, description="Filter by district name"),
    state: Optional[str] = Query(None, description="Filter by state name"),
    start_date: Optional[str] = Query(None, description="Start date ISO format"),
    end_date: Optional[str] = Query(None, description="End date ISO format"),
    language: Optional[str] = Query(None, description="Filter by language code"),
    channel: Optional[str] = Query(None, description="Filter by channel")
) -> RiskDistributionResponse:
    repo = get_analytics_repository()
    return repo.get_risk_distribution(
        district=district,
        state=state,
        start_date=start_date,
        end_date=end_date,
        language=language,
        channel=channel
    )


@router.get(
    "/flag-frequency",
    response_model=FlagFrequencyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Risk Flag Category Frequency Breakdown",
    description="Returns occurrence counts and percentage breakdown for extracted distress flags (intimidation, fear, trauma, etc.)."
)
async def get_flag_frequency(
    district: Optional[str] = Query(None, description="Filter by district name"),
    state: Optional[str] = Query(None, description="Filter by state name"),
    start_date: Optional[str] = Query(None, description="Start date ISO format"),
    end_date: Optional[str] = Query(None, description="End date ISO format"),
    risk_tier: Optional[str] = Query(None, description="Filter by risk tier"),
    language: Optional[str] = Query(None, description="Filter by language code"),
    channel: Optional[str] = Query(None, description="Filter by channel")
) -> FlagFrequencyResponse:
    repo = get_analytics_repository()
    return repo.get_flag_frequency(
        district=district,
        state=state,
        start_date=start_date,
        end_date=end_date,
        risk_tier=risk_tier,
        language=language,
        channel=channel
    )


@router.get(
    "/channel-language-volume",
    response_model=ChannelLanguageVolumeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Case Volume Breakdown by Channel and Language",
    description="Returns case volume counts grouped by ingestion channel and caller language."
)
async def get_channel_language_volume(
    district: Optional[str] = Query(None, description="Filter by district name"),
    state: Optional[str] = Query(None, description="Filter by state name"),
    start_date: Optional[str] = Query(None, description="Start date ISO format"),
    end_date: Optional[str] = Query(None, description="End date ISO format"),
    risk_tier: Optional[str] = Query(None, description="Filter by risk tier")
) -> ChannelLanguageVolumeResponse:
    repo = get_analytics_repository()
    return repo.get_channel_language_volume(
        district=district,
        state=state,
        start_date=start_date,
        end_date=end_date,
        risk_tier=risk_tier
    )
