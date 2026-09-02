"""
Analytics Repository Interface & Implementations (Mock & SQLAlchemy)
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Provides high-performance aggregation queries over historical SVI scores
and risk assessment records WITHOUT recomputing raw audio/text.
==============================================================================
"""

import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from api.analytics.schemas import (
    SVITrendItem,
    SVITrendResponse,
    RiskDistributionItem,
    RiskDistributionResponse,
    FlagFrequencyItem,
    FlagFrequencyResponse,
    ChannelLanguageVolumeItem,
    ChannelLanguageVolumeResponse
)


class AnalyticsRepository(ABC):
    """Abstract Repository Interface for Perception Analytics."""

    @abstractmethod
    def get_svi_trend(
        self,
        district: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        risk_tier: Optional[str] = None,
        language: Optional[str] = None,
        channel: Optional[str] = None,
        period: str = "weekly"
    ) -> SVITrendResponse:
        pass

    @abstractmethod
    def get_risk_distribution(
        self,
        district: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        language: Optional[str] = None,
        channel: Optional[str] = None
    ) -> RiskDistributionResponse:
        pass

    @abstractmethod
    def get_flag_frequency(
        self,
        district: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        risk_tier: Optional[str] = None,
        language: Optional[str] = None,
        channel: Optional[str] = None
    ) -> FlagFrequencyResponse:
        pass

    @abstractmethod
    def get_channel_language_volume(
        self,
        district: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        risk_tier: Optional[str] = None
    ) -> ChannelLanguageVolumeResponse:
        pass


class MockAnalyticsRepository(AnalyticsRepository):
    """
    Mock Repository pre-populated with realistic historical helpline perception records.
    Used for local development, API testing, and standalone evaluation.
    """

    def __init__(self):
        self.records: List[Dict[str, Any]] = self._generate_mock_dataset()

    @staticmethod
    def _generate_mock_dataset() -> List[Dict[str, Any]]:
        """Generates deterministic mock historical perception records."""
        dataset = []
        base_date = datetime(2026, 8, 1, 10, 0, 0)
        
        sample_districts = [
            ("Central Delhi", "Delhi"),
            ("Jaipur Urban", "Rajasthan"),
            ("Lucknow East", "Uttar Pradesh"),
            ("Chennai Central", "Tamil Nadu"),
            ("Patna Rural", "Bihar")
        ]
        sample_channels = ["ivrs", "phone", "chat", "portal", "mobile_app"]
        sample_languages = ["hi", "en", "ta"]

        # 120 deterministic mock historical records spanning 4 weeks
        for i in range(120):
            dist, st = sample_districts[i % len(sample_districts)]
            ch = sample_channels[i % len(sample_channels)]
            lang = sample_languages[i % len(sample_languages)]
            created = base_date + timedelta(days=i // 4, hours=(i % 4) * 3)
            
            # Deterministic SVI score curve
            svi_score = int(15 + (i * 7) % 80)
            if svi_score <= 24:
                tier = "Low"
            elif svi_score <= 49:
                tier = "Moderate"
            elif svi_score <= 74:
                tier = "High"
            else:
                tier = "Critical"

            # Assign flags based on score severity
            flags = []
            if svi_score >= 50:
                flags.append("intimidation")
                flags.append("fear")
            if svi_score >= 75:
                flags.append("suicidal_ideation")
                flags.append("extreme_vulnerability")
            if svi_score < 50:
                flags.append("isolation")

            dataset.append({
                "case_id": 1000 + i,
                "created_at": created,
                "date_str": created.strftime("%Y-%m-%d"),
                "week_str": created.strftime("%Y-W%W"),
                "district": dist,
                "state": st,
                "channel": ch,
                "language": lang,
                "svi_score": svi_score,
                "risk_tier": tier,
                "flags": flags
            })
        return dataset

    def _filter_records(
        self,
        district: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        risk_tier: Optional[str] = None,
        language: Optional[str] = None,
        channel: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        filtered = self.records
        if district:
            filtered = [r for r in filtered if r["district"].lower() == district.lower()]
        if state:
            filtered = [r for r in filtered if r["state"].lower() == state.lower()]
        if risk_tier:
            filtered = [r for r in filtered if r["risk_tier"].lower() == risk_tier.lower()]
        if language:
            filtered = [r for r in filtered if r["language"].lower() == language.lower()]
        if channel:
            filtered = [r for r in filtered if r["channel"].lower() == channel.lower()]
        if start_date:
            filtered = [r for r in filtered if r["date_str"] >= start_date]
        if end_date:
            filtered = [r for r in filtered if r["date_str"] <= end_date]
        return filtered

    def get_svi_trend(
        self,
        district: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        risk_tier: Optional[str] = None,
        language: Optional[str] = None,
        channel: Optional[str] = None,
        period: str = "weekly"
    ) -> SVITrendResponse:
        records = self._filter_records(district, state, start_date, end_date, risk_tier, language, channel)
        
        grouped: Dict[str, List[int]] = {}
        for r in records:
            key = r["week_str"] if period == "weekly" else r["date_str"]
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(r["svi_score"])

        items = []
        for time_key in sorted(grouped.keys()):
            scores = grouped[time_key]
            avg_svi = round(sum(scores) / len(scores), 2) if scores else 0.0
            items.append(
                SVITrendItem(
                    time_period=time_key,
                    district=district,
                    state=state,
                    average_svi=avg_svi,
                    case_count=len(scores)
                )
            )

        return SVITrendResponse(
            period_type=period,
            total_cases_analyzed=len(records),
            trends=items
        )

    def get_risk_distribution(
        self,
        district: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        language: Optional[str] = None,
        channel: Optional[str] = None
    ) -> RiskDistributionResponse:
        records = self._filter_records(district, state, start_date, end_date, None, language, channel)
        total = len(records)
        
        tier_counts = {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0}
        for r in records:
            tier_counts[r["risk_tier"]] = tier_counts.get(r["risk_tier"], 0) + 1

        dist_items = []
        for t_name in ["Low", "Moderate", "High", "Critical"]:
            cnt = tier_counts.get(t_name, 0)
            pct = round((cnt / total * 100.0), 2) if total > 0 else 0.0
            dist_items.append(RiskDistributionItem(risk_tier=t_name, count=cnt, percentage=pct))

        return RiskDistributionResponse(total_cases=total, distribution=dist_items)

    def get_flag_frequency(
        self,
        district: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        risk_tier: Optional[str] = None,
        language: Optional[str] = None,
        channel: Optional[str] = None
    ) -> FlagFrequencyResponse:
        records = self._filter_records(district, state, start_date, end_date, risk_tier, language, channel)
        
        flag_counts: Dict[str, int] = {}
        total_flags = 0

        for r in records:
            for f in r["flags"]:
                flag_counts[f] = flag_counts.get(f, 0) + 1
                total_flags += 1

        flag_items = []
        for fname, cnt in sorted(flag_counts.items(), key=lambda x: x[1], reverse=True):
            pct = round((cnt / total_flags * 100.0), 2) if total_flags > 0 else 0.0
            flag_items.append(FlagFrequencyItem(flag_name=fname, count=cnt, percentage=pct))

        return FlagFrequencyResponse(total_flags_count=total_flags, flags=flag_items)

    def get_channel_language_volume(
        self,
        district: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        risk_tier: Optional[str] = None
    ) -> ChannelLanguageVolumeResponse:
        records = self._filter_records(district, state, start_date, end_date, risk_tier, None, None)
        total = len(records)

        grouped: Dict[tuple, int] = {}
        for r in records:
            key = (r["channel"], r["language"])
            grouped[key] = grouped.get(key, 0) + 1

        vol_items = []
        for (ch, lang), cnt in sorted(grouped.items(), key=lambda x: x[1], reverse=True):
            vol_items.append(ChannelLanguageVolumeItem(channel=ch, language=lang, count=cnt))

        return ChannelLanguageVolumeResponse(total_cases=total, volumes=vol_items)


# Global singleton repository instance
_GLOBAL_ANALYTICS_REPO: Optional[AnalyticsRepository] = None

def get_analytics_repository() -> AnalyticsRepository:
    global _GLOBAL_ANALYTICS_REPO
    if _GLOBAL_ANALYTICS_REPO is None:
        _GLOBAL_ANALYTICS_REPO = MockAnalyticsRepository()
    return _GLOBAL_ANALYTICS_REPO
