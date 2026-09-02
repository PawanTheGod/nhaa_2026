from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import Cases, Notifications
from app.schemas import NotificationOut
from app.routes.audit import log_action
from app.routes.websocket import ws_manager
from app.services.notifications import (
    confirm_and_dispatch,
    process_risk_assessment,
)

router = APIRouter(tags=["notifications"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


class OfficerDecisionIn(BaseModel):
    confirmed_by: str


@router.post(
    "/risk-assessments/{risk_assessment_id}/dispatch",
    response_model=list[NotificationOut],
)
async def dispatch_for_risk_assessment(
    risk_assessment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Called after a new risk assessment is created (by the websocket listener,
    or directly by whichever process just POSTed to /risk-assessments/).

    Creates Notifications rows per the tier -> recipient mapping.
    Idempotent: calling this twice for the same risk_assessment_id is safe
    and will not create duplicate notifications.
    """
    try:
        created = await process_risk_assessment(db, risk_assessment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if created:
        await ws_manager.broadcast(
            {
                "event": "notifications_created",
                "data": {
                    "risk_assessment_id": risk_assessment_id,
                    "count": len(created),
                    "recipients": [n.recipient_role.value for n in created],
                },
            }
        )
    return created


@router.post(
    "/cases/{case_id}/officer-decision",
    response_model=list[NotificationOut],
)
async def officer_decision(
    case_id: int,
    decision: OfficerDecisionIn,
    db: AsyncSession = Depends(get_db),
):
    """
    HARD CONFIRMATION GATE for Critical-tier cases.

    An officer must call this (via Pawan's CaseDetailPanel 'Confirm action'
    button) before any Critical-tier notification is actually dispatched.
    There is no other way to move a confirmation-required notification out
    of 'pending' -- see app/services/notifications.py::confirm_and_dispatch.
    """
    case_result = await db.execute(select(Cases).where(Cases.id == case_id))
    if case_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Case not found")

    dispatched = await confirm_and_dispatch(db, case_id, decision.confirmed_by)

    await log_action(
        db,
        actor=decision.confirmed_by,
        action="officer_decision_confirmed",
        case_id=case_id,
        details={"notifications_dispatched": len(dispatched)},
    )

    if dispatched:
        await ws_manager.broadcast(
            {
                "event": "notifications_dispatched",
                "data": {
                    "case_id": case_id,
                    "confirmed_by": decision.confirmed_by,
                    "count": len(dispatched),
                    "recipients": [n.recipient_role.value for n in dispatched],
                },
            }
        )
    return dispatched


@router.get("/cases/{case_id}/notifications", response_model=list[NotificationOut])
async def list_notifications_for_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """All notifications (sent + pending) for a given case, for the test log
    and for Pawan's CaseDetailPanel to show current dispatch state."""
    result = await db.execute(
        select(Notifications).where(Notifications.case_id == case_id)
    )
    return result.scalars().all()
