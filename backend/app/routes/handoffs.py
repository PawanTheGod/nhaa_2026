"""
app/routes/handoffs.py
───────────────────────
Tier handoffs, SP case locking, judiciary directives, and case examine updates.
Supports the multi-tier workflow: IO → ACP/DSP → SP → Director/Judiciary → SWO.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_officer, require_role
from app.auth.tokens import TokenPayload
from app.database import get_db
from app.models import AuditLogs, CaseHandoffs, Cases, CaseStatus, Officers
from app.schemas import (
    CaseExamineUpdate, CaseLockIn, CaseOut, HandoffCreate, HandoffOut, JudiciaryForwardIn,
)

router = APIRouter(tags=["Hierarchical Workflow"])


@router.post("/cases/{case_id}/handoff", response_model=HandoffOut, status_code=status.HTTP_201_CREATED)
async def create_case_handoff(
    case_id: int,
    payload: HandoffCreate,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    """Transfer case jurisdiction or supervisory responsibility to another tier/officer."""
    res = await db.execute(select(Cases).where(Cases.id == case_id))
    case = res.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case #{case_id} not found")

    off_res = await db.execute(select(Officers).where(Officers.username == officer.sub))
    db_officer = off_res.scalar_one_or_none()
    from_officer_id = db_officer.id if db_officer else None

    # Determine tier level adjustment
    tier_levels = {
        "operator": 0,
        "io": 0,
        "acp": 1,
        "dsp": 1,
        "sp": 2,
        "director": 3,
        "ig": 3,
        "judiciary": 4,
        "swo": 5,
    }
    new_level = tier_levels.get(payload.to_tier.lower(), case.current_level)
    if new_level is not None:
        case.current_level = new_level

    handoff = CaseHandoffs(
        case_id=case_id,
        from_officer_id=from_officer_id,
        to_officer_id=payload.to_officer_id,
        from_tier=officer.role,
        to_tier=payload.to_tier,
        handoff_notes=payload.handoff_notes,
    )
    db.add(handoff)

    # Log in audit
    db.add(
        AuditLogs(
            actor=f"{officer.role}:{officer.sub}",
            action="case_handoff",
            case_id=case_id,
            details={
                "from_tier": officer.role,
                "to_tier": payload.to_tier,
                "notes": payload.handoff_notes,
            },
        )
    )
    await db.commit()
    await db.refresh(handoff)
    return handoff


@router.get("/cases/{case_id}/handoffs", response_model=list[HandoffOut])
async def list_case_handoffs(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    """Get the full chronological handoff history for a case."""
    res = await db.execute(
        select(CaseHandoffs)
        .where(CaseHandoffs.case_id == case_id)
        .order_by(CaseHandoffs.created_at.asc())
    )
    return res.scalars().all()


@router.post("/cases/{case_id}/lock", response_model=CaseOut)
async def lock_case_by_sp(
    case_id: int,
    payload: Optional[CaseLockIn] = None,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    """SP locks the case record before forwarding to Judiciary review."""
    res = await db.execute(select(Cases).where(Cases.id == case_id))
    case = res.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case #{case_id} not found")

    off_res = await db.execute(select(Officers).where(Officers.username == officer.sub))
    db_officer = off_res.scalar_one_or_none()
    officer_id = db_officer.id if db_officer else None

    case.is_locked = True
    case.locked_by = officer_id
    case.locked_at = datetime.now(timezone.utc)
    case.status = CaseStatus.locked

    notes = payload.notes if payload else "Locked by SP for Judiciary forwarding"
    db.add(
        AuditLogs(
            actor=f"{officer.role}:{officer.sub}",
            action="case_locked",
            case_id=case_id,
            details={"notes": notes},
        )
    )
    await db.commit()
    await db.refresh(case)
    return case


@router.post("/cases/{case_id}/unlock", response_model=CaseOut)
async def unlock_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    """Unlock a locked case for further modifications."""
    res = await db.execute(select(Cases).where(Cases.id == case_id))
    case = res.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case #{case_id} not found")

    case.is_locked = False
    case.locked_by = None
    case.locked_at = None
    case.status = CaseStatus.in_progress

    db.add(
        AuditLogs(
            actor=f"{officer.role}:{officer.sub}",
            action="case_unlocked",
            case_id=case_id,
            details={},
        )
    )
    await db.commit()
    await db.refresh(case)
    return case


@router.post("/cases/{case_id}/forward-to-swo", response_model=CaseOut)
async def forward_case_to_swo(
    case_id: int,
    payload: JudiciaryForwardIn,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    """Judiciary officer forwards directive to Social Welfare Officer (SWO) for rehabilitation."""
    res = await db.execute(select(Cases).where(Cases.id == case_id))
    case = res.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case #{case_id} not found")

    case.forwarded_to_swo = True
    case.judiciary_directive = payload.directive
    case.status = CaseStatus.adjudicated

    # Record handoff
    off_res = await db.execute(select(Officers).where(Officers.username == officer.sub))
    db_officer = off_res.scalar_one_or_none()
    db.add(
        CaseHandoffs(
            case_id=case_id,
            from_officer_id=db_officer.id if db_officer else None,
            from_tier=officer.role,
            to_tier="swo",
            handoff_notes=f"Judiciary Directive: {payload.directive}\nNotes: {payload.notes or ''}",
        )
    )

    db.add(
        AuditLogs(
            actor=f"{officer.role}:{officer.sub}",
            action="judiciary_forward_swo",
            case_id=case_id,
            details={"directive": payload.directive, "notes": payload.notes},
        )
    )
    await db.commit()
    await db.refresh(case)
    return case


@router.patch("/cases/{case_id}/examine", response_model=CaseOut)
async def update_case_examine(
    case_id: int,
    payload: CaseExamineUpdate,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    """Update case examination form fields (victim name, location, dates, exit report, summary)."""
    res = await db.execute(select(Cases).where(Cases.id == case_id))
    case = res.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case #{case_id} not found")

    if case.is_locked and officer.role not in ("sp", "ig", "director", "judiciary", "super_admin"):
        raise HTTPException(status_code=403, detail="Case is locked by SP. Modifications restricted.")

    update_dict = payload.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if hasattr(case, key):
            setattr(case, key, value)

    db.add(
        AuditLogs(
            actor=f"{officer.role}:{officer.sub}",
            action="case_examine_updated",
            case_id=case_id,
            details={"updated_fields": list(update_dict.keys())},
        )
    )
    await db.commit()
    await db.refresh(case)
    return case
