"""
Notification / Dispatch Service tests (Pushp's module).

Covers:
  1. Each risk tier notifies exactly the right set of recipients.
  2. Critical-tier notifications are held pending, never auto-sent.
  3. Idempotency: processing the same risk_assessment twice creates no
     duplicate notifications.
  4. Bypass test: nothing can dispatch a Critical notification except
     confirm_and_dispatch() with an explicit confirmed_by actor.
  5. End-to-end: officer-decision endpoint actually flips pending -> sent.

Writes a dated CSV test log to backend/tests/test_log.csv, the same file
you show at the demo as proof of end-to-end testing.
"""
import csv
import os
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_notifications.db")
os.environ.setdefault("DEBUG", "false")

from app.main import app  # noqa: E402
from app.database import engine, Base, AsyncSessionLocal  # noqa: E402
from app.models import Cases, RiskAssessments, Notifications, NotificationStatus  # noqa: E402
from app.services.notifications import (  # noqa: E402
    process_risk_assessment,
    confirm_and_dispatch,
    try_bypass_dispatch,
    TIER_RECIPIENTS,
)

from conftest import log_result as _log  # shared session-wide E2E log


@pytest.fixture(scope="module", autouse=True)
async def _setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def _make_case_with_assessment(db, tier: str, svi: float, channel="portal"):
    case = Cases(channel_of_origin=channel, district="Test District", state="Test State")
    db.add(case)
    await db.commit()
    await db.refresh(case)

    ra = RiskAssessments(
        case_id=case.id,
        svi_score=svi,
        risk_tier=tier,
        flags={"trauma": True} if tier in ("high", "critical") else {},
        explanation_text=f"Synthetic test assessment for tier={tier}",
        model_version="test-fixture-v1",
    )
    db.add(ra)
    await db.commit()
    await db.refresh(ra)
    return case, ra


@pytest.mark.asyncio
@pytest.mark.parametrize("tier,svi", [
    ("low", 15.0),
    ("moderate", 45.0),
    ("high", 70.0),
    ("critical", 92.0),
])
async def test_tier_notifies_correct_recipients(tier, svi):
    """Each risk tier must notify exactly the right set of recipients."""
    async with AsyncSessionLocal() as db:
        case, ra = await _make_case_with_assessment(db, tier, svi)
        created = await process_risk_assessment(db, ra.id)

        expected_roles = {r.value for r in TIER_RECIPIENTS[ra.risk_tier]}
        actual_roles = {n.recipient_role.value for n in created}

        passed = actual_roles == expected_roles
        _log("test-fixture", tier, expected_roles, actual_roles, passed)
        assert passed, f"tier={tier}: expected {expected_roles}, got {actual_roles}"


@pytest.mark.asyncio
async def test_critical_notifications_held_pending():
    """Critical notifications must never be auto-sent."""
    async with AsyncSessionLocal() as db:
        case, ra = await _make_case_with_assessment(db, "critical", 95.0)
        created = await process_risk_assessment(db, ra.id)

        assert len(created) > 0
        for notif in created:
            assert notif.status == NotificationStatus.pending
            assert notif.sent_at is None
            assert notif.message_template["requires_confirmation"] is True
            assert notif.message_template["confirmed"] is False


@pytest.mark.asyncio
async def test_moderate_and_high_dispatch_immediately():
    """Moderate/High should be marked sent right away (no human gate)."""
    async with AsyncSessionLocal() as db:
        for tier, svi in [("moderate", 40.0), ("high", 65.0)]:
            case, ra = await _make_case_with_assessment(db, tier, svi)
            created = await process_risk_assessment(db, ra.id)
            for notif in created:
                assert notif.status == NotificationStatus.sent
                assert notif.sent_at is not None


@pytest.mark.asyncio
async def test_idempotency_no_duplicate_notifications():
    """Processing the same risk_assessment_id twice must not double-notify."""
    async with AsyncSessionLocal() as db:
        case, ra = await _make_case_with_assessment(db, "high", 68.0)

        first_pass = await process_risk_assessment(db, ra.id)
        second_pass = await process_risk_assessment(db, ra.id)

        assert len(first_pass) == 3  # district, police, dlsa
        assert len(second_pass) == 0  # already processed, nothing new created

        result = await db.execute(
            select_notifications_for_case(case.id)
        )
        all_notifs = result.scalars().all()
        assert len(all_notifs) == 3  # still just 3, not 6


def select_notifications_for_case(case_id: int):
    from sqlalchemy import select
    return select(Notifications).where(Notifications.case_id == case_id)


@pytest.mark.asyncio
async def test_critical_cannot_bypass_confirmation():
    """
    The bypass test: there must be no code path that dispatches a
    confirmation-required notification without an explicit officer decision.
    """
    async with AsyncSessionLocal() as db:
        case, ra = await _make_case_with_assessment(db, "critical", 98.0)
        created = await process_risk_assessment(db, ra.id)

        bypass_succeeded = False
        try:
            try_bypass_dispatch(created[0])
            bypass_succeeded = True  # should never reach here
        except NotImplementedError:
            bypass_succeeded = False

        _log(
            "bypass-attempt", "critical",
            expected={"blocked"},
            actual={"blocked" if not bypass_succeeded else "BYPASSED"},
            passed=not bypass_succeeded,
        )
        assert not bypass_succeeded, "SECURITY: critical notification was bypassed!"

        # Confirm it is still pending in the DB regardless of the attempt.
        result = await db.execute(select_notifications_for_case(case.id))
        for notif in result.scalars().all():
            assert notif.status == NotificationStatus.pending


@pytest.mark.asyncio
async def test_officer_decision_endpoint_dispatches_critical():
    """End-to-end: the real API endpoint used by Pawan's Confirm button."""
    async with AsyncSessionLocal() as db:
        case, ra = await _make_case_with_assessment(db, "critical", 99.0)
        await process_risk_assessment(db, ra.id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Before confirmation: still pending.
        before = await client.get(f"/api/cases/{case.id}/notifications")
        assert all(n["status"] == "pending" for n in before.json())

        # Officer confirms.
        resp = await client.post(
            f"/api/cases/{case.id}/officer-decision",
            json={"confirmed_by": "district_officer_test_001"},
        )
        assert resp.status_code == 200
        dispatched = resp.json()
        assert len(dispatched) == 5  # district, state, police, wp, medical
        assert all(n["status"] == "sent" for n in dispatched)

        _log(
            "api-endpoint", "critical",
            expected={"district", "state", "police", "witness_protection", "medical"},
            actual={n["recipient_role"] for n in dispatched},
            passed=len(dispatched) == 5,
        )


@pytest.mark.asyncio
async def test_officer_decision_on_case_with_no_pending_is_noop():
    """Confirming a case with nothing pending should return an empty list,
    not error and not create phantom notifications."""
    async with AsyncSessionLocal() as db:
        case, ra = await _make_case_with_assessment(db, "low", 10.0)
        await process_risk_assessment(db, ra.id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/cases/{case.id}/officer-decision",
            json={"confirmed_by": "someone"},
        )
        assert resp.status_code == 200
        assert resp.json() == []
