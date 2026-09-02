"""
app/routes/admin_panel.py
─────────────────────────
The seven Admin Panel endpoints Aditya is responsible for.
These wrap Vinit's underlying DB queries but enforce JWT-based scope
automatically — no raw role/district/state query params needed.

Endpoints:
    GET  /api/cases                – role-scoped list (all 9 roles)
    GET  /api/cases/{id}           – full detail incl. AI fields
    GET  /api/sla-status           – per-case SLA countdown
    GET  /api/stats/district       – district-level aggregates
    GET  /api/stats/state          – state-level aggregates
    GET  /api/stats/national       – national-level aggregates (ministry only)
    POST /api/officer-decision     – record decision / override / mark-actioned
"""

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select, case as sa_case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.middleware import (
    build_case_filter,
    enforce_scope,
    get_current_officer,
    require_role,
    RESPONDER_ROLES,
)
from app.auth.tokens import TokenPayload
from app.database import AsyncSessionLocal
from app.models import (
    Cases, CaseStatus, OfficerRole, RiskAssessments, RiskTier, SlaDeadlines,
)
from app.routes.audit import log_action

router = APIRouter(tags=["admin-panel"])


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── Shared serialisers ────────────────────────────────────────────────────────

def _latest_ra(case: Cases) -> Optional[RiskAssessments]:
    """Return the most-recent RiskAssessment for a case (None if none exist)."""
    if not case.risk_assessments:
        return None
    return sorted(case.risk_assessments, key=lambda r: r.created_at, reverse=True)[0]


def _serialize_notification(n: Any) -> dict[str, Any]:
    return {
        "id": n.id,
        "case_id": n.case_id,
        "recipient_role": n.recipient_role.value if hasattr(n.recipient_role, "value") else str(n.recipient_role),
        "channel": n.channel,
        "sent_at": n.sent_at.isoformat() if n.sent_at else None,
        "status": n.status.value if hasattr(n.status, "value") else str(n.status),
    }


def _case_list_item(case: Cases) -> dict[str, Any]:
    """Serialise a case for GET /api/cases list response."""
    ra = _latest_ra(case)
    recommended_action = case.recommended_action
    if not recommended_action and ra and ra.flags:
        recommended_action = ra.flags.get("recommended_action")

    notifications = [_serialize_notification(n) for n in (case.notifications or [])]

    is_actioned = case.status in (CaseStatus.resolved, CaseStatus.closed)

    responder_type = None
    try:
        if case.assigned_officer and case.assigned_officer.role:
            responder_type = case.assigned_officer.role.value
    except Exception:
        pass

    return {
        "id": case.id,
        "case_id": case.id,
        "status": case.status.value if case.status else None,
        "current_level": case.current_level,
        "channel_of_origin": case.channel_of_origin.value if case.channel_of_origin else None,
        "district": case.district,
        "state": case.state,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        "risk_tier": case.risk_tier.value if case.risk_tier else None,
        "svi_score": float(case.svi_score) if case.svi_score is not None else None,
        "recommended_action": recommended_action,
        "is_silent_signal": case.is_silent_signal,
        "incident_description": case.incident_description,
        "assigned_officer_id": case.assigned_officer_id,
        "responder_type": responder_type,
        "actioned": is_actioned,
        "flags": ra.flags if ra else {},
        "explanation_text": ra.explanation_text if ra else None,
        "notifications": notifications,

        "risk_assessments": [
            {
                "id": r.id,
                "svi_score": float(r.svi_score),
                "risk_tier": r.risk_tier.value,
                "explanation_text": r.explanation_text,
                "flags": r.flags,
                "created_at": r.created_at.isoformat(),
                "model_version": r.model_version,
            }
            for r in sorted(case.risk_assessments or [], key=lambda r: r.created_at, reverse=True)
        ],
    }


def _case_detail(case: Cases) -> dict[str, Any]:
    """Serialise a case for GET /api/cases/{id} — includes full AI fields."""
    base = _case_list_item(case)
    ra = _latest_ra(case)
    base.update({
        "incident_date": case.incident_date.isoformat() if case.incident_date else None,
        "language": case.language,
        "victim_id": case.victim_id,
        "model_version": ra.model_version if ra else None,
    })
    return base



# ─────────────────────────────────────────────────────────────────────────────
# GET /api/cases
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/cases",
    summary="List cases — JWT-scoped by role",
    operation_id="admin_list_cases",
    description=(
        "Returns cases the logged-in officer is allowed to see.\n\n"
        "- **operator / district** – cases in their district\n"
        "- **state** – cases in their state\n"
        "- **ministry** – all cases\n"
        "- **Responders** (police / dlsa / medical / counselor / witness_protection) "
        "  – ONLY cases where they are the assigned officer\n\n"
        "Role/district/state are read from the JWT — query params can be used as additional filters."
    ),
)
async def list_cases(
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
    # Optional filters
    role: Optional[str] = Query(None, description="Optional role filter"),
    district: Optional[str] = Query(None, description="Filter by district"),
    state: Optional[str] = Query(None, description="Filter by state"),
    status: Optional[CaseStatus] = Query(None, description="Filter by case status"),
    risk_tier: Optional[RiskTier] = Query(None, description="Filter by risk tier"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    scope_clauses = build_case_filter(officer)

    query = (
        select(Cases)
        .options(
            selectinload(Cases.risk_assessments),
            selectinload(Cases.notifications),
            selectinload(Cases.assigned_officer),
        )
        .where(*scope_clauses)
        .order_by(Cases.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if district and officer.role in ("state", "ministry"):
        query = query.where(Cases.district == district)
    if state and officer.role == "ministry":
        query = query.where(Cases.state == state)
    if status:
        query = query.where(Cases.status == status)
    if risk_tier:
        query = query.where(Cases.risk_tier == risk_tier)

    result = await db.execute(query)
    cases = result.scalars().unique().all()
    return [_case_list_item(c) for c in cases]



# ─────────────────────────────────────────────────────────────────────────────
# GET /api/cases/{id}
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/cases/{case_id}",
    summary="Full case detail including AI SVI/risk/explanation — JWT-scoped",
    operation_id="admin_get_case",
)
async def get_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    result = await db.execute(
        select(Cases)
        .options(
            selectinload(Cases.risk_assessments),
            selectinload(Cases.notifications),
            selectinload(Cases.assigned_officer),
        )
        .where(Cases.id == case_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Scope check — responders can only see their own assigned case
    enforce_scope(case, officer)

    return _case_detail(case)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/cases/{case_id}/full
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/cases/{case_id}/full",
    summary="Full case detail including Case, History (Audit), and AI routing/copilot data",
)
async def get_full_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    result = await db.execute(
        select(Cases)
        .options(
            selectinload(Cases.risk_assessments),
            selectinload(Cases.notifications),
            selectinload(Cases.assigned_officer),
            selectinload(Cases.audit_logs),
        )
        .where(Cases.id == case_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    enforce_scope(case, officer)

    base = _case_detail(case)
    
    # Include audit logs (history)
    base["history"] = [
        {
            "id": a.id,
            "actor": a.actor,
            "action": a.action,
            "timestamp": a.timestamp.isoformat(),
            "details": a.details,
        }
        for a in sorted(case.audit_logs or [], key=lambda x: x.timestamp, reverse=True)
    ]
    return base


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/cases/{case_id}/allowed-actions
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/cases/{case_id}/allowed-actions",
    summary="Get allowed actions for a case based on status, current level, and user role",
)
async def get_allowed_actions(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    result = await db.execute(select(Cases).where(Cases.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    enforce_scope(case, officer)

    actions = []
    
    if officer.role in RESPONDER_ROLES:
        return {"allowed_actions": ["mark_actioned"]}

    if case.status == CaseStatus.closed or case.status == CaseStatus.resolved:
        return {"allowed_actions": []}
    
    if case.status == CaseStatus.new or case.status == CaseStatus.in_progress:
        actions.extend(["escalate", "resolve"])
    elif case.status == CaseStatus.escalated:
        current_lvl = case.current_level or "police"
        if current_lvl == officer.role:
            actions.extend(["escalate", "resolve"])
        elif officer.role == "ministry" and current_lvl == "ministry":
            actions.extend(["resolve"])

    return {"allowed_actions": actions}


class CaseActionIn(BaseModel):
    action: str
    notes: Optional[str] = None

# ─────────────────────────────────────────────────────────────────────────────
# POST /api/cases/{case_id}/action
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/cases/{case_id}/action",
    summary="Process an action (e.g. escalate, resolve) on a case",
)
async def process_case_action(
    case_id: int,
    payload: CaseActionIn,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    result = await db.execute(
        select(Cases)
        .options(
            selectinload(Cases.risk_assessments),
            selectinload(Cases.notifications),
            selectinload(Cases.assigned_officer)
        )
        .where(Cases.id == case_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    enforce_scope(case, officer)

    action = payload.action.lower()
    previous_status = case.status.value if case.status else None
    
    if action == "resolve":
        case.status = CaseStatus.resolved
    elif action == "escalate":
        case.status = CaseStatus.escalated
        hierarchy = ["operator", "police", "district", "state", "ministry"]
        current_lvl = case.current_level or ("police" if officer.role == "operator" else officer.role)
        current_idx = hierarchy.index(current_lvl) if current_lvl in hierarchy else 0
        if current_idx < len(hierarchy) - 1:
            case.current_level = hierarchy[current_idx + 1]
    elif action == "close":
        case.status = CaseStatus.closed
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    await db.commit()
    await db.refresh(case)

    await log_action(
        db,
        actor=officer.sub,
        action=f"case_action_{action}",
        case_id=case.id,
        details={"previous_status": previous_status, "new_status": case.status.value, "notes": payload.notes, "current_level": case.current_level},
    )

    if ws_manager is not None:
        await ws_manager.broadcast({
            "event": "case_updated",
            "data": _case_list_item(case),
        })

    return {"message": "Action processed", "status": case.status.value, "current_level": case.current_level}


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/sla-status
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/sla-status",
    summary="Per-case SLA countdown (operator, district, state, ministry)",
    description=(
        "Returns SLA deadline status for cases in the officer's scope. "
        "Responder roles are not permitted — SLA monitoring is a supervisory function. "
        "Use `?case_id=X` to get the SLA status for a single case."
    ),
)
async def sla_status(
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(
        require_role("operator", "district", "state", "ministry")
    ),
    case_id: Optional[int] = Query(None, description="Limit to a single case"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    now = datetime.now(timezone.utc)

    # Build case-scope filter
    case_scope = build_case_filter(officer)

    # Query SLA deadlines joined to cases
    dl_query = (
        select(SlaDeadlines)
        .join(Cases, Cases.id == SlaDeadlines.case_id)
        .where(*case_scope)
        .order_by(SlaDeadlines.due_date.asc())
        .limit(limit)
        .offset(offset)
    )
    if case_id is not None:
        dl_query = dl_query.where(SlaDeadlines.case_id == case_id)

    result = await db.execute(dl_query)
    deadlines = result.scalars().all()

    # Group by case_id
    grouped: dict[int, list[dict]] = {}
    for dl in deadlines:
        # due_date may be timezone-naive (SQLite stores UTC without tz info)
        due = dl.due_date
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)

        hours_remaining = (due - now).total_seconds() / 3600
        entry = {
            "deadline_type": dl.deadline_type,
            "due_date": due.isoformat(),
            "hours_remaining": round(hours_remaining, 2),
            "is_overdue": hours_remaining < 0,
            "met": dl.met,
            "resolved_at": dl.resolved_at.isoformat() if dl.resolved_at else None,
        }
        grouped.setdefault(dl.case_id, []).append(entry)

    return [
        {"case_id": cid, "deadlines": dls}
        for cid, dls in grouped.items()
    ]


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/stats/district
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/stats/district",
    summary="District-level aggregate stats (district, state, ministry)",
)
async def stats_district(
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(
        require_role("district", "state", "ministry")
    ),
):
    """
    Returns aggregate stats for the officer's district (district role),
    or all districts within the officer's state (state role),
    or all districts nationally (ministry role).
    """
    query = select(
        Cases.district,
        func.count().label("total_cases"),
        func.sum(sa_case((Cases.status == CaseStatus.resolved, 1), else_=0)).label("resolved"),
        func.sum(sa_case((Cases.risk_tier == RiskTier.critical, 1), else_=0)).label("critical"),
        func.sum(sa_case((Cases.risk_tier == RiskTier.high, 1), else_=0)).label("high"),
        func.avg(Cases.svi_score).label("avg_svi"),
    ).where(Cases.district.is_not(None))

    # Scope
    if officer.role == OfficerRole.district.value and officer.district:
        query = query.where(Cases.district == officer.district)
    elif officer.role == OfficerRole.state.value and officer.state:
        query = query.where(Cases.state == officer.state)
    # ministry — no filter

    query = query.group_by(Cases.district).order_by(func.count().desc())
    result = await db.execute(query)

    rows = []
    for row in result.fetchall():
        total = row.total_cases or 0
        resolved = int(row.resolved or 0)
        rows.append({
            "district": row.district,
            "total_cases": total,
            "resolved": resolved,
            "resolution_rate": round(resolved / total * 100, 1) if total else 0.0,
            "critical": int(row.critical or 0),
            "high": int(row.high or 0),
            "avg_svi": round(float(row.avg_svi), 2) if row.avg_svi else None,
        })
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/stats/state
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/stats/state",
    summary="State-level aggregate stats (state, ministry)",
)
async def stats_state(
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(require_role("state", "ministry")),
):
    """
    Returns aggregate stats for the officer's state (state role)
    or all states (ministry role).
    """
    query = select(
        Cases.state,
        func.count().label("total_cases"),
        func.sum(sa_case((Cases.status == CaseStatus.resolved, 1), else_=0)).label("resolved"),
        func.sum(sa_case((Cases.risk_tier == RiskTier.critical, 1), else_=0)).label("critical"),
        func.sum(sa_case((Cases.risk_tier == RiskTier.high, 1), else_=0)).label("high"),
        func.avg(Cases.svi_score).label("avg_svi"),
    ).where(Cases.state.is_not(None))

    if officer.role == OfficerRole.state.value and officer.state:
        query = query.where(Cases.state == officer.state)
    # ministry — no filter

    query = query.group_by(Cases.state).order_by(func.count().desc())
    result = await db.execute(query)

    rows = []
    for row in result.fetchall():
        total = row.total_cases or 0
        resolved = int(row.resolved or 0)
        rows.append({
            "state": row.state,
            "total_cases": total,
            "resolved": resolved,
            "resolution_rate": round(resolved / total * 100, 1) if total else 0.0,
            "critical": int(row.critical or 0),
            "high": int(row.high or 0),
            "avg_svi": round(float(row.avg_svi), 2) if row.avg_svi else None,
        })
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/stats/national
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/stats/national",
    summary="National aggregate stats — ministry only",
)
async def stats_national(
    db: AsyncSession = Depends(get_db),
    _officer: TokenPayload = Depends(require_role("ministry")),
):
    """
    Top-level national KPIs for the Ministry dashboard.
    Returns total cases, tier breakdown, resolution rate, and per-channel counts.
    """
    # Overall counts
    total_result = await db.execute(select(func.count()).select_from(Cases))
    total = total_result.scalar_one()

    tier_result = await db.execute(
        select(Cases.risk_tier, func.count().label("count"))
        .where(Cases.risk_tier.is_not(None))
        .group_by(Cases.risk_tier)
    )
    tier_breakdown = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
    for tier, count in tier_result.fetchall():
        tier_breakdown[tier.value if hasattr(tier, "value") else tier] = count

    resolved_result = await db.execute(
        select(func.count()).where(Cases.status == CaseStatus.resolved)
    )
    resolved = resolved_result.scalar_one()

    channel_result = await db.execute(
        select(Cases.channel_of_origin, func.count().label("count"))
        .group_by(Cases.channel_of_origin)
    )
    channel_breakdown: dict[str, int] = {}
    for ch, count in channel_result.fetchall():
        channel_breakdown[ch.value if hasattr(ch, "value") else ch] = count

    avg_svi_result = await db.execute(select(func.avg(Cases.svi_score)))
    avg_svi = avg_svi_result.scalar_one()

    return {
        "total_cases": total,
        "resolved": resolved,
        "resolution_rate": round(resolved / total * 100, 1) if total else 0.0,
        "tier_breakdown": tier_breakdown,
        "channel_breakdown": channel_breakdown,
        "avg_svi": round(float(avg_svi), 2) if avg_svi else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/officer-decision
# ─────────────────────────────────────────────────────────────────────────────

class OfficerDecisionIn(BaseModel):
    case_id: int
    decision_type: str  # "categorise" | "override" | "mark_actioned"
    category: Optional[str] = None             # e.g. "domestic_violence"
    override_risk_tier: Optional[str] = None   # triggers AI consistency check
    notes: Optional[str] = None
    responder_action: Optional[str] = None     # for responder 'mark actioned' flow


class OfficerDecisionOut(BaseModel):
    recorded: bool
    audit_id: int
    consistency_check_triggered: bool


@router.post(
    "/officer-decision",
    response_model=OfficerDecisionOut,
    summary="Record officer categorisation, override, or responder action",
    description=(
        "Used by:\n"
        "- **Pawan's Operator screen** — officer categorises or manually overrides AI risk tier\n"
        "- **Pawan's Responder screen** — responder marks a case 'actioned'\n\n"
        "If `override_risk_tier` is present, Aatmman's AI consistency-check "
        "function will be triggered (stubbed until Aatmman's module is ready).\n\n"
        "Every decision is written to the audit log."
    ),
)
async def officer_decision(
    decision: OfficerDecisionIn,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    # Verify the case exists and officer can see it
    result = await db.execute(
        select(Cases)
        .options(selectinload(Cases.risk_assessments))
        .where(Cases.id == decision.case_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    enforce_scope(case, officer)

    # Build audit details payload
    details: dict[str, Any] = {
        "decision_type": decision.decision_type,
        "officer_role": officer.role,
        "officer_id": officer.sub,
    }
    if decision.category:
        details["category"] = decision.category
    if decision.override_risk_tier:
        details["override_risk_tier"] = decision.override_risk_tier
    if decision.notes:
        details["notes"] = decision.notes
    if decision.responder_action:
        details["responder_action"] = decision.responder_action

    # ── Apply override if requested ───────────────────────────────────────────
    consistency_triggered = False
    if decision.override_risk_tier:
        try:
            new_tier = RiskTier(decision.override_risk_tier)
            case.risk_tier = new_tier
            await db.commit()
            await db.refresh(case)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid risk_tier value: {decision.override_risk_tier}",
            )

        # ── Stub: call Aatmman's consistency-check (replace when module ready) ─
        # from app.services.ai_consistency import run_consistency_check
        # await run_consistency_check(case_id=case.id, new_tier=new_tier, actor=officer.sub)
        consistency_triggered = True

    # ── Write to audit log ────────────────────────────────────────────────────
    from sqlalchemy import insert
    from app.models import AuditLogs

    insert_result = await db.execute(
        insert(AuditLogs).values(
            actor=officer.sub,
            action="officer_decision",
            case_id=decision.case_id,
            details=details,
            timestamp=datetime.now(timezone.utc),
        ).returning(AuditLogs.id)
    )
    await db.commit()
    audit_id = insert_result.scalar_one()

    return OfficerDecisionOut(
        recorded=True,
        audit_id=audit_id,
        consistency_check_triggered=consistency_triggered,
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/decisions/confirm (Pawan: Critical confirm human-in-the-loop)
# ─────────────────────────────────────────────────────────────────────────────

from app.services.notifications import confirm_and_dispatch
from app.routes.websocket import ws_manager


class CriticalConfirmIn(BaseModel):
    case_id: int
    action: str = "confirm_critical_dispatch"
    officer_id: Optional[str] = None


@router.post(
    "/decisions/confirm",
    summary="Confirm critical dispatch (human-in-the-loop)",
    description=(
        "Called from Pawan's CaseDetailPanel when an officer clicks 'Confirm action' "
        "on a Critical-tier case to release pending dispatches."
    ),
)
async def confirm_critical_decision(
    payload: CriticalConfirmIn,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    case_res = await db.execute(
        select(Cases).where(Cases.id == payload.case_id)
    )
    case = case_res.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    enforce_scope(case, officer)

    confirmed_by = payload.officer_id or officer.name or officer.sub
    dispatched = await confirm_and_dispatch(db, payload.case_id, confirmed_by)

    await log_action(
        db,
        actor=confirmed_by,
        action="critical_dispatch_confirmed",
        case_id=payload.case_id,
        details={
            "action": payload.action,
            "dispatched_count": len(dispatched),
            "recipients": [n.recipient_role.value for n in dispatched],
        },
    )

    if dispatched and ws_manager is not None:
        await ws_manager.broadcast({
            "event": "notifications_dispatched",
            "data": {
                "case_id": payload.case_id,
                "confirmed_by": confirmed_by,
                "count": len(dispatched),
                "recipients": [n.recipient_role.value for n in dispatched],
            },
        })

    return {
        "confirmed": True,
        "case_id": payload.case_id,
        "action": payload.action,
        "dispatched_count": len(dispatched),
        "recipients": [n.recipient_role.value for n in dispatched],
    }


# ─────────────────────────────────────────────────────────────────────────────
# PATCH /api/decisions/{case_id}/actioned (Pawan: Responder mark actioned)
# ─────────────────────────────────────────────────────────────────────────────

class ResponderActionedIn(BaseModel):
    responder_type: Optional[str] = None
    actioned: bool = True
    notes: Optional[str] = None


@router.patch(
    "/decisions/{case_id}/actioned",
    summary="Mark responder task as actioned",
    description=(
        "Called from Pawan's ResponderTaskCard when a responder officer "
        "(Police, DLSA, Medical, Counselor, Witness Protection) clicks 'Mark Actioned'."
    ),
)
async def responder_mark_actioned(
    case_id: int,
    payload: ResponderActionedIn,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    case_res = await db.execute(
        select(Cases)
        .options(
            selectinload(Cases.risk_assessments),
            selectinload(Cases.notifications),
            selectinload(Cases.assigned_officer),
        )
        .where(Cases.id == case_id)
    )
    case = case_res.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    enforce_scope(case, officer)

    if payload.actioned and case.status == CaseStatus.new:
        case.status = CaseStatus.in_progress

    await db.commit()
    await db.refresh(case)

    actor_name = officer.name or officer.sub
    await log_action(
        db,
        actor=actor_name,
        action="responder_task_actioned",
        case_id=case_id,
        details={
            "responder_type": payload.responder_type or officer.role,
            "actioned": payload.actioned,
            "notes": payload.notes,
        },
    )

    if ws_manager is not None:
        await ws_manager.broadcast({
            "event": "case_updated",
            "data": _case_list_item(case),
        })

    return {
        "case_id": case_id,
        "responder_type": payload.responder_type or officer.role,
        "actioned": payload.actioned,
        "status": case.status.value,
    }

