import json
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import Cases, CaseStatus, OfficerRole, RiskTier
from app.schemas import CaseCreate, CaseDetail, CaseOut, CaseUpdate
from app.routes.audit import log_action
from app.routes.websocket import ws_manager

router = APIRouter(prefix="/cases", tags=["cases"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def _send_ws(event: str, payload: dict[str, Any]):
    await ws_manager.broadcast(
        {"event": event, "data": payload, "timestamp": datetime.utcnow().isoformat()}
    )


def _serialize_case(case: Cases) -> dict[str, Any]:
    return {
        "id": case.id,
        "channel_of_origin": case.channel_of_origin.value if case.channel_of_origin else None,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        "status": case.status.value if case.status else None,
        "district": case.district,
        "state": case.state,
        "incident_description": case.incident_description,
        "language": case.language,
        "is_silent_signal": case.is_silent_signal,
        "svi_score": float(case.svi_score) if case.svi_score else None,
        "risk_tier": case.risk_tier.value if case.risk_tier else None,
        "recommended_action": case.recommended_action,
    }


@router.post("/", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_db),
    role: Optional[str] = Query(None, description="Simulated caller role for audit"),
    district: Optional[str] = Query(None, description="Simulated caller district"),
    state: Optional[str] = Query(None, description="Simulated caller state"),
):
    """
    Create a new case. Called by **any** channel (Portal, Chatbot, IVRS, Mobile App).
    """
    case = Cases(**case_data.model_dump(exclude_unset=True))
    db.add(case)
    await db.commit()
    await db.refresh(case)

    actor = f"{role or 'system'}:{district or ''}:{state or ''}".strip(":")
    await log_action(
        db,
        actor=actor,
        action="case_created",
        case_id=case.id,
        details={"channel": case.channel_of_origin.value, "district": case.district, "state": case.state},
    )

    await _send_ws("case_created", _serialize_case(case))

    result = await db.execute(
        select(Cases).options(selectinload(Cases.risk_assessments)).where(Cases.id == case.id)
    )
    return result.scalar_one()


@router.get("/", response_model=list[CaseOut])
async def list_cases(
    db: AsyncSession = Depends(get_db),
    role: str = Query(
        default="ministry",
        description="Simulated role of the caller (operator, district, state, ministry). Replace with JWT in Step 6.",
    ),
    district: Optional[str] = Query(None, description="Filter by district (used when role=district)"),
    state: Optional[str] = Query(None, description="Filter by state (used when role=state)"),
    status: Optional[CaseStatus] = Query(None),
    risk_tier: Optional[RiskTier] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    List cases, filtered by the caller's role.

    **Role-based row filtering** (Step 6 — query-param based for now;
    Aditya will replace with JWT enforcement):

    - **operator** – only cases this operator created/handled (filtered by `district` param)
    - **district**  – all cases in the operator's district
    - **state**     – all cases in the officer's state
    - **ministry**  – every case
    """
    query = select(Cases).options(selectinload(Cases.risk_assessments)).order_by(Cases.created_at.desc()).limit(limit).offset(offset)

    if role in ("operator", "district", "dsp"):
        if district:
            query = query.where(
                (Cases.district == district) | (Cases.district == "Unknown") | (Cases.district.is_(None))
            )
    elif role == "state":
        if state:
            query = query.where(
                (Cases.state == state) | (Cases.state == "Unknown") | (Cases.state.is_(None))
            )
    # ministry sees all

    if status:
        query = query.where(Cases.status == status)
    if risk_tier:
        query = query.where(Cases.risk_tier == risk_tier)

    result = await db.execute(query)
    cases = result.scalars().unique().all()
    return cases


@router.get("/{case_id}", response_model=CaseDetail)
async def get_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Full detail of a single case, including **all** risk assessments.
    """
    result = await db.execute(
        select(Cases).options(selectinload(Cases.risk_assessments)).where(Cases.id == case_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.patch("/{case_id}", response_model=CaseOut)
async def update_case(
    case_id: int,
    case_data: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    role: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
):
    """
    Update a case (typically status). Sends a real-time WebSocket event.
    """
    result = await db.execute(
        select(Cases).options(selectinload(Cases.risk_assessments)).where(Cases.id == case_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    before_status = case.status

    update_data = case_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    await db.commit()
    await db.refresh(case)

    actor = f"{role or 'system'}:{district or ''}:{state or ''}".strip(":")
    await log_action(
        db,
        actor=actor,
        action="status_updated" if "status" in update_data else "case_updated",
        case_id=case.id,
        details={"field": update_data, "previous_status": before_status.value if before_status else None},
    )

    await _send_ws("case_updated", _serialize_case(case))
    return case
