from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import Cases, CaseStatus, RiskTier

router = APIRouter(prefix="/stats", tags=["stats"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/cases", response_model=dict)
async def get_case_stats(
    db: AsyncSession = Depends(get_db),
    role: str = Query(default="ministry"),
    district: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
):
    """
    Aggregate case statistics for admin dashboards.
    - State screen: role=state&state=Delhi
    - District screen: role=district&district=Central Delhi
    - Ministry screen: role=ministry
    """
    query = select(Cases)
    if role == "district" and district:
        query = query.where(Cases.district == district)
    elif role == "state" and state:
        query = query.where(Cases.state == state)
    # ministry sees all

    total_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total_cases = total_result.scalar_one()

    tier_result = await db.execute(
        select(
            Cases.risk_tier,
            func.count().label("count"),
        )
        .where(Cases.risk_tier.is_not(None))
        .group_by(Cases.risk_tier)
    )
    tier_breakdown = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
    for tier, count in tier_result.fetchall():
        tier_breakdown[tier] = count

    resolved_result = await db.execute(
        select(func.count()).where(Cases.status == CaseStatus.resolved)
    )
    resolved = resolved_result.scalar_one()
    resolution_rate = round((resolved / total_cases * 100), 1) if total_cases else 0.0

    pending_sla = await db.execute(
        select(func.count()).where(
            Cases.status.in_([CaseStatus.new, CaseStatus.in_progress]),
            Cases.risk_tier.in_([RiskTier.high, RiskTier.critical]),
        )
    )
    pending_sla_count = pending_sla.scalar_one()

    return {
        "total_cases": total_cases,
        "tier_breakdown": tier_breakdown,
        "resolution_rate": resolution_rate,
        "resolved_count": resolved,
        "pending_sla": pending_sla_count,
    }


@router.get("/trend", response_model=list)
async def get_case_trend(
    db: AsyncSession = Depends(get_db),
    role: str = Query(default="ministry"),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    weeks: int = Query(default=4, ge=1, le=52),
):
    """
    Weekly trend of case volume and average SVI over the last N weeks.
    """
    cutoff = datetime.utcnow() - timedelta(weeks=weeks)

    query = select(Cases).where(Cases.created_at >= cutoff)
    if role == "state" and state:
        query = query.where(Cases.state == state)
    elif role == "district" and district:
        query = query.where(Cases.district == district)

    result = await db.execute(query.order_by(Cases.created_at))
    cases = result.scalars().all()

    buckets = {}
    for c in cases:
        week_str = c.created_at.strftime("%Y-W%W") if c.created_at else "unknown"
        if week_str not in buckets:
            buckets[week_str] = {"week": week_str, "cases": 0, "svi_sum": 0.0, "critical": 0}
        buckets[week_str]["cases"] += 1
        if c.svi_score is not None:
            buckets[week_str]["svi_sum"] += float(c.svi_score)
        if c.risk_tier == RiskTier.critical:
            buckets[week_str]["critical"] += 1

    return sorted(
        [
            {
                "week": v["week"],
                "cases": v["cases"],
                "sviAvg": round(v["svi_sum"] / v["cases"], 1) if v["cases"] else 0,
                "critical": v["critical"],
            }
            for v in buckets.values()
        ],
        key=lambda x: x["week"],
    )


@router.get("/districts", response_model=list)
async def get_district_comparison(
    db: AsyncSession = Depends(get_db),
    role: str = Query(default="ministry"),
    state: Optional[str] = Query(None),
):
    """
    District-level comparison: case counts, resolution rate, high-risk count.
    """
    query = select(
        Cases.district,
        func.count().label("cases"),
        func.sum(case((Cases.status == CaseStatus.resolved, 1), else_=0)).label("resolved"),
    )
    if state:
        query = query.where(Cases.state == state)
    query = query.where(Cases.district.is_not(None)).group_by(Cases.district)

    result = await db.execute(query)
    districts = []
    for row in result.fetchall():
        rate = round(float(row.resolved) / float(row.cases) * 100, 1) if row.cases else 0.0
        districts.append({
            "district": row.district,
            "cases": row.cases,
            "resolved": row.resolved,
            "resolutionRate": rate,
            "highRisk": 0,
        })
    return sorted(districts, key=lambda d: d.cases, reverse=True)


@router.get("/states", response_model=list)
async def get_state_comparison(
    db: AsyncSession = Depends(get_db),
):
    """
    State-by-state comparison for the Ministry dashboard.
    """
    query = select(
        Cases.state,
        func.count().label("cases"),
        func.sum(case((Cases.status == CaseStatus.resolved, 1), else_=0)).label("resolved"),
        func.sum(case((Cases.risk_tier == RiskTier.critical, 1), else_=0)).label("critical"),
    ).where(Cases.state.is_not(None)).group_by(Cases.state)

    result = await db.execute(query)
    states = []
    for row in result.fetchall():
        rate = round(float(row.resolved) / float(row.cases) * 100, 1) if row.cases else 0.0
        states.append({
            "state": row.state,
            "cases": row.cases,
            "resolved": row.resolved,
            "resolutionRate": rate,
            "highRisk": 0,
            "critical": row.critical,
        })
    return sorted(states, key=lambda s: s.cases, reverse=True)
