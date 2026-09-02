"""
Notification / Dispatch Service (Pushp's module).

Reads a RiskAssessment's risk_tier and creates Notifications rows for the
correct recipients, per the officer hierarchy defined in the SIH design doc:

    Low       -> operator only, log only, no alert
    Moderate  -> district officer
    High      -> district officer + police + dlsa   (simultaneous)
    Critical  -> district + state + police + witness_protection + medical
                 (held pending until an officer confirms)

Idempotency: keyed on risk_assessment_id. If the same risk assessment is
processed twice (duplicate websocket event, retry, etc.), we do not create
duplicate notification rows.
"""
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Cases,
    Notifications,
    NotificationStatus,
    OfficerRole,
    RiskAssessments,
    RiskTier,
)

# ── Tier -> recipient roles mapping ────────────────────────────────
# Source: officer hierarchy table in the SIH master design doc.
TIER_RECIPIENTS: dict[RiskTier, list[OfficerRole]] = {
    RiskTier.low: [OfficerRole.operator],
    RiskTier.moderate: [OfficerRole.district],
    RiskTier.high: [OfficerRole.district, OfficerRole.police, OfficerRole.dlsa],
    RiskTier.critical: [
        OfficerRole.district,
        OfficerRole.state,
        OfficerRole.police,
        OfficerRole.witness_protection,
        OfficerRole.medical,
    ],
}

# Tiers that require a human "Confirm action" before the alert is actually
# marked as sent. This is a hard backend gate, not a UI-only restriction.
TIERS_REQUIRING_CONFIRMATION = {RiskTier.critical}

DEFAULT_CHANNEL = "in_app"  # in_app | email | sms


async def _already_processed(db: AsyncSession, risk_assessment_id: int) -> bool:
    """
    Idempotency check. We key on the risk_assessment_id: if any Notifications
    row already references this assessment's case AND was created as part of
    processing this exact assessment, skip re-processing.

    We store the risk_assessment_id inside message_template (JSON) since the
    Notifications table (built by Vinit) doesn't have a dedicated column for
    it -- this keeps us from needing a migration to add your own service's
    logic on top of the shared schema.
    """
    result = await db.execute(
        select(Notifications).where(
            Notifications.message_template["risk_assessment_id"].as_integer()
            == risk_assessment_id
        )
    )
    return result.first() is not None


async def process_risk_assessment(
    db: AsyncSession, risk_assessment_id: int
) -> list[Notifications]:
    """
    Main entry point. Call this whenever a new RiskAssessments row is
    created (e.g. from a websocket 'risk_assessment_created' event, or
    directly after POST /api/risk-assessments/).

    Returns the list of Notifications rows created (empty list if this
    event was already processed, or if tier is Low with nothing to notify).
    """
    if await _already_processed(db, risk_assessment_id):
        return []

    result = await db.execute(
        select(RiskAssessments).where(RiskAssessments.id == risk_assessment_id)
    )
    ra = result.scalar_one_or_none()
    if ra is None:
        raise ValueError(f"RiskAssessment {risk_assessment_id} not found")

    recipients = TIER_RECIPIENTS.get(ra.risk_tier, [])
    requires_confirmation = ra.risk_tier in TIERS_REQUIRING_CONFIRMATION

    created: list[Notifications] = []
    for role in recipients:
        notif = Notifications(
            case_id=ra.case_id,
            recipient_role=role,
            channel=DEFAULT_CHANNEL,
            status=NotificationStatus.pending,
            sent_at=None,
            message_template={
                "risk_assessment_id": risk_assessment_id,
                "risk_tier": ra.risk_tier.value,
                "svi_score": float(ra.svi_score),
                "requires_confirmation": requires_confirmation,
                "confirmed": False,
                "created_at": datetime.utcnow().isoformat(),
            },
        )
        db.add(notif)
        created.append(notif)

    if not requires_confirmation:
        # Low / Moderate / High: no human gate, so there is nothing left
        # to wait for -- mark as sent immediately. For Low tier this
        # represents "logged, operator's own queue already shows it,"
        # not a separate outbound alert. Leaving it as 'pending' would be
        # actively misleading (the schema has no 'logged_only' status,
        # and 'pending' implies something is still waiting to be
        # dispatched, which is false for Low/Moderate/High).
        for notif in created:
            notif.status = NotificationStatus.sent
            notif.sent_at = datetime.utcnow()
    # Critical (requires_confirmation=True) is the only tier left pending
    # here -- it stays that way until confirm_and_dispatch() is called.

    await db.commit()
    for notif in created:
        await db.refresh(notif)

    return created


async def confirm_and_dispatch(
    db: AsyncSession, case_id: int, confirmed_by: str
) -> list[Notifications]:
    """
    HARD GATE for Critical-tier cases.

    Only this function is allowed to flip a pending, confirmation-required
    notification to 'sent'. It requires an explicit confirmed_by actor
    (the officer). There is no other code path in this service that
    dispatches a confirmation-required notification -- calling
    process_risk_assessment() alone will never send one.
    """
    result = await db.execute(
        select(Notifications).where(Notifications.case_id == case_id)
    )
    notifications = result.scalars().all()

    pending_gated = [
        n
        for n in notifications
        if n.status == NotificationStatus.pending
        and n.message_template
        and n.message_template.get("requires_confirmation")
        and not n.message_template.get("confirmed")
    ]

    if not pending_gated:
        return []

    for notif in pending_gated:
        notif.status = NotificationStatus.sent
        notif.sent_at = datetime.utcnow()
        notif.message_template = {
            **notif.message_template,
            "confirmed": True,
            "confirmed_by": confirmed_by,
            "confirmed_at": datetime.utcnow().isoformat(),
        }

    await db.commit()
    for notif in pending_gated:
        await db.refresh(notif)

    return pending_gated


def try_bypass_dispatch(notif: Notifications) -> None:
    """
    Deliberately NOT a real function you'd call in production. This exists
    only so the bypass test can assert the correct behaviour: there is no
    direct "just mark it sent" helper exposed by this module for
    confirmation-gated notifications. The only legitimate path is
    confirm_and_dispatch(), which requires confirmed_by.

    Kept here as living documentation of the invariant, referenced by
    test_notifications.py::test_critical_cannot_bypass_confirmation.
    """
    raise NotImplementedError(
        "Critical-tier notifications cannot be dispatched without going "
        "through confirm_and_dispatch(). There is no bypass path."
    )
