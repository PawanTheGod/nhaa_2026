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


@router.post("/from-perception", response_model=RiskAssessmentOut, status_code=status.HTTP_201_CREATED)
async def create_risk_assessment_from_perception(
    perception_data: dict,
    db: AsyncSession = Depends(get_db),
    actor: str = Query(default="vedika_perception", description="Actor performing the assessment"),
):
    """
    Primary entry point for the **full AI pipeline** (Vedika → Aatmman → Pushp).

    Accepts Vedika's raw PerceptionOutputContract JSON, runs Aatmman's agent
    decision engine (tier refinement, action recommendations, OpenRouter explanation),
    and saves the enriched RiskAssessment to the database.

    The Silent Distress Signal is handled transparently: if ``is_silent_signal``
    is set on the case, it forces the tier to Critical without exposing anything
    in the visible transcript.
    """
    from app.services.agent.decision_engine import determine_risk_tier, recommend_actions
    from app.services.agent.openrouter import generate_explanation

    # Extract fields from Vedika's PerceptionOutputContract
    case_id = perception_data.get("case_id")
    if not case_id:
        raise HTTPException(status_code=400, detail="case_id is required in perception payload")

    svi_data = perception_data.get("svi", {})
    svi_score = float(svi_data.get("score", 0))
    flags = list(perception_data.get("flags", []))  # [{name, confidence, signals, source}, ...]

    # Verify case exists
    case_result = await db.execute(select(Cases).where(Cases.id == int(case_id)))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    # --- Silent Distress Signal handling ---
    # If the case was already flagged (e.g. by DTMF sequence, hidden keyword, or long-press),
    # inject a synthetic flag so the decision engine forces Critical.
    # We do NOT modify the visible transcript or case description.
    if case.is_silent_signal:
        flags.append({
            "name": "silent_distress_signal",
            "confidence": 1.0,
            "signals": ["Silent distress signal activated by victim"],
            "source": ["system"]
        })

    # --- Agent Decision Engine ---
    # Step 1: Determine final tier (may upgrade Vedika's suggestion based on flag overrides)
    final_tier = determine_risk_tier(svi_score, flags)

    # Step 2: Recommend actions based on tier + specific flags
    actions = recommend_actions(final_tier, flags)

    # Step 3: Generate specific plain-language explanation via OpenRouter
    explanation = await generate_explanation(svi_score, final_tier.value, actions, flags)

    # Step 4: Build flags dict for DB storage (Vinit schema: {flag_name: confidence, ...})
    flags_for_db = {f.get("name"): f.get("confidence") for f in flags if f.get("name")}
    flags_for_db["recommended_action"] = ", ".join(actions)

    # --- Persist enriched RiskAssessment ---
    ra = RiskAssessments(
        case_id=int(case_id),
        svi_score=svi_score,
        risk_tier=final_tier,
        flags=flags_for_db,
        explanation_text=explanation,
        model_version=perception_data.get("schema_version", "1.0"),
    )
    db.add(ra)

    case.svi_score = svi_score
    case.risk_tier = final_tier
    case.recommended_action = ", ".join(actions)

    await db.commit()
    await db.refresh(ra)
    await db.refresh(case)

    await log_action(
        db,
        actor=actor,
        action="risk_assessed_via_agent",
        case_id=ra.case_id,
        details={
            "svi_score": float(ra.svi_score),
            "risk_tier": ra.risk_tier.value,
            "actions": actions,
            "silent_signal": case.is_silent_signal,
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
                "recommended_actions": actions,
                "created_at": ra.created_at.isoformat(),
            },
            "timestamp": case.updated_at.isoformat() if case.updated_at else None,
        })

    # --- Dispatch to Pushp's notification gate ---
    # Critical tier stays PENDING until a human officer confirms.
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
