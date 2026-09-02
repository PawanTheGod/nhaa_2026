"""
Full end-to-end integration test: all 4 intake channels x all 4 risk
tiers, through the complete pipeline:

    channel POST /cases -> POST /risk-assessments -> notification
    service creates Notifications rows -> (Critical only) officer
    confirms via /officer-decision -> notifications flip to sent

This is the test that answers, concretely:
  - "Does a complaint from any channel reach the same Admin Panel view?"
  - "Does each risk tier notify exactly the right set of people?"
  - "Does Critical always wait for human confirmation?"

Every case in this file is logged to the shared E2E test log
(tests/test_log.csv) via conftest.log_result, alongside the tier-level
tests in test_notifications.py.
"""
import os

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_sync.db")
os.environ.setdefault("DEBUG", "false")

from app.main import app  # noqa: E402
from app.database import engine, Base, AsyncSessionLocal  # noqa: E402
from app.models import Cases, RiskAssessments  # noqa: E402
from app.services.notifications import TIER_RECIPIENTS  # noqa: E402
from conftest import log_result  # noqa: E402

FOUR_CHANNELS = ["portal", "chatbot", "ivrs", "mobile_app"]
FOUR_TIERS = [("low", 12.0), ("moderate", 42.0), ("high", 68.0), ("critical", 94.0)]


@pytest.fixture(scope="module", autouse=True)
async def _setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("channel", FOUR_CHANNELS)
@pytest.mark.parametrize("tier,svi", FOUR_TIERS)
async def test_full_pipeline_per_channel_and_tier(channel, tier, svi):
    """
    For each (channel, tier) pair: create a case as if it came from that
    channel, post a risk assessment at that tier, confirm the right
    notifications were created, and — for Critical — confirm as an
    officer and verify the notifications actually dispatch.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Complaint arrives via this channel.
        case_resp = await client.post(
            "/api/cases/",
            params={"role": "operator", "district": "Test District", "state": "Test State"},
            json={
                "channel_of_origin": channel,
                "district": "Test District",
                "state": "Test State",
                "incident_description": f"E2E test case via {channel}, tier={tier}",
            },
        )
        assert case_resp.status_code == 201, case_resp.text
        case_id = case_resp.json()["id"]

        # 2. AI module (simulated) posts the risk assessment.
        ra_resp = await client.post(
            "/api/risk-assessments/",
            params={"actor": "ai_module_test"},
            json={
                "case_id": case_id,
                "svi_score": svi,
                "risk_tier": tier,
                "flags": {"trauma": True} if tier in ("high", "critical") else {},
                "explanation_text": f"E2E synthetic assessment for {channel}/{tier}",
                "model_version": "e2e-test-fixture",
            },
        )
        assert ra_resp.status_code == 201, ra_resp.text

        # 3. Check notifications were created for the right recipients.
        notif_resp = await client.get(f"/api/cases/{case_id}/notifications")
        assert notif_resp.status_code == 200
        notifications = notif_resp.json()

        expected_roles = {r.value for r in TIER_RECIPIENTS[tier]}
        actual_roles = {n["recipient_role"] for n in notifications}
        recipients_match = actual_roles == expected_roles

        # 4. Critical: must be pending, must require officer confirmation.
        if tier == "critical":
            all_pending = all(n["status"] == "pending" for n in notifications)
            log_result(channel, tier, expected_roles, actual_roles,
                        recipients_match and all_pending)
            assert all_pending, f"{channel}/{tier}: expected pending, got statuses={[n['status'] for n in notifications]}"

            # Officer confirms.
            confirm_resp = await client.post(
                f"/api/cases/{case_id}/officer-decision",
                json={"confirmed_by": f"test_officer_{channel}"},
            )
            assert confirm_resp.status_code == 200
            dispatched = confirm_resp.json()
            all_sent = all(n["status"] == "sent" for n in dispatched)
            log_result(f"{channel}-post-confirm", tier,
                       expected_roles, {n["recipient_role"] for n in dispatched},
                       all_sent and len(dispatched) == len(expected_roles))
            assert all_sent
        else:
            # Low/Moderate/High: should already be sent, no confirmation needed.
            all_sent = all(n["status"] == "sent" for n in notifications)
            log_result(channel, tier, expected_roles, actual_roles,
                        recipients_match and all_sent)
            assert all_sent, f"{channel}/{tier}: expected auto-sent, got {[n['status'] for n in notifications]}"

        assert recipients_match, f"{channel}/{tier}: expected {expected_roles}, got {actual_roles}"


@pytest.mark.asyncio
async def test_all_four_channels_appear_in_same_case_list():
    """All 4 channels must land in the same shared case list, confirming
    there is one pipeline, not four disconnected ones."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created_ids = []
        for channel in FOUR_CHANNELS:
            resp = await client.post(
                "/api/cases/",
                params={"role": "operator", "district": "Unified District", "state": "Unified State"},
                json={
                    "channel_of_origin": channel,
                    "district": "Unified District",
                    "state": "Unified State",
                    "incident_description": f"Unified list check via {channel}",
                },
            )
            assert resp.status_code == 201
            created_ids.append(resp.json()["id"])

        list_resp = await client.get(
            "/api/cases/",
            params={"role": "operator", "district": "Unified District", "state": "Unified State", "limit": 50},
        )
        assert list_resp.status_code == 200
        listed_ids = {c["id"] for c in list_resp.json()}

        all_present = all(cid in listed_ids for cid in created_ids)
        log_result(
            "all-4-channels", "n/a",
            expected={str(i) for i in created_ids},
            actual={str(i) for i in listed_ids if i in created_ids},
            passed=all_present,
        )
        assert all_present, "not all 4 channel-origin cases appeared in the shared case list"
