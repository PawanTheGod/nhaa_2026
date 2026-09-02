from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import Cases, RiskAssessments
from app.schemas import RiskAssessmentCreate, RiskAssessmentOut
from app.routes.audit import log_action
from app.routes.websocket import ws_manager
from app.services.notifications import process_risk_assessment

router = APIRouter(prefix="/risk-assessments", tags=["risk-assessments"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/", response_model=RiskAssessmentOut, status_code=status.HTTP_201_CREATED)
async def create_risk_assessment(
    ra_data: RiskAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    actor: str = Query(default="ai_module", description="Actor performing the assessment — typically the AI module"),
):
    """
    Called **only** by the AI module (Aatmman / Vedika).

    Links an SVI score + risk tier + flags + explanation text to a case.
    """
    case_result = await db.execute(select(Cases).where(Cases.id == ra_data.case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    ra = RiskAssessments(**ra_data.model_dump(exclude_unset=True))
    db.add(ra)

    case.svi_score = ra.svi_score
    case.risk_tier = ra.risk_tier
    if ra.flags and "recommended_action" in ra.flags:
        case.recommended_action = ra.flags["recommended_action"]

    await db.commit()
    await db.refresh(ra)
    await db.refresh(case)

    await log_action(
        db,
        actor=actor,
        action="risk_assessed",
        case_id=ra.case_id,
        details={
            "svi_score": float(ra.svi_score),
            "risk_tier": ra.risk_tier.value,
            "model_version": ra.model_version,
        },
    )

    if ws_manager is not None:
        await ws_manager.broadcast({
            "event": "risk_assessment_created",
            "data": {
                "id": ra.id,
                "case_id": ra.case_id,
                "svi_score": float(ra.svi_score),
                "risk_tier": ra.risk_tier.value,
                "explanation_text": ra.explanation_text,
                "created_at": ra.created_at.isoformat(),
            },
            "timestamp": case.updated_at.isoformat() if case.updated_at else None,
        })

    # Pushp's notification/dispatch service: create Notifications rows for
    # the correct recipients based on risk_tier. Idempotent by design, so
    # this is safe even if risk assessments are ever re-broadcast.
    created_notifs = await process_risk_assessment(db, ra.id)
    if created_notifs and ws_manager is not None:
        await ws_manager.broadcast({
            "event": "notifications_created",
            "data": {
                "risk_assessment_id": ra.id,
                "case_id": ra.case_id,
                "count": len(created_notifs),
                "recipients": [n.recipient_role.value for n in created_notifs],
            },
        })

    return ra


@router.get("/case/{case_id}", response_model=list[RiskAssessmentOut])
async def get_risk_assessments(
    case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Return all risk assessments for a given case.
    """
    result = await db.execute(
        select(RiskAssessments).where(RiskAssessments.case_id == case_id).order_by(RiskAssessments.created_at.desc())
    )
    return result.scalars().all()
