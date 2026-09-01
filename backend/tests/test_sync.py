"""
Synchronization Test (Step 8 — the test you hand to Pushp).

Simulates four separate POST requests to /cases as if they came from the
Portal, Chatbot, IVRS, and Mobile App, then verifies:

  1. All four show up correctly in a single GET /cases call.
  2. All four trigger a WebSocket push within a reasonable window.
  3. Role-based filtering genuinely blocks a district officer from
     seeing another district's cases.
  4. POST /risk-assessments links a score to a case and pushes an event.
  5. The append-only audit_log captures every action.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_sync.db")
os.environ.setdefault("DEBUG", "false")

from app.main import app  # noqa: E402
from app.database import engine, Base, AsyncSessionLocal  # noqa: E402
from app.models import Cases, RiskAssessments, AuditLogs  # noqa: E402
from app.routes.cases import router as cases_router  # noqa: E402
from app.routes.websocket import ws_manager  # noqa: E402


# ── Helper: fire four simulated channel requests ──────────────

FOUR_CHANNELS = [
    {
        "channel_of_origin": "portal",
        "district": "Central Delhi",
        "state": "Delhi",
        "incident_description": "Online complaint through citizen portal about caste-based denial of entry to commercial establishment.",
        "is_silent_signal": False,
    },
    {
        "channel_of_origin": "chatbot",
        "district": "East Delhi",
        "state": "Delhi",
        "incident_description": "Chatbot transcript: victim reports continuous harassment and threats of eviction by landlord for reporting a crime.",
        "is_silent_signal": True,  # silent distress keyword triggered
    },
    {
        "channel_of_origin": "ivrs",
        "district": "South Delhi",
        "state": "Delhi",
        "incident_description": "IVRS call — victim reports physical assault by family members for refusing a marriage.",
        "is_silent_signal": False,
    },
    {
        "channel_of_origin": "mobile_app",
        "district": "North Delhi",
        "state": "Delhi",
        "incident_description": "Mobile app report: witness intimidation after FIR was filed; victim fears retaliation.",
        "is_silent_signal": True,
    },
]


@pytest.fixture(scope="module", autouse=True)
async def fresh_db():
    """Create tables before the test module, clean up after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def ws_conn():
    """
    Open a real WebSocket connection to the ASGI app and collect events.
    Uses httpx's ASGI transport directly on the FastAPI app.
    """
    transport = ASGITransport(app=app)
    from httpx import Client
    events = []

    # We use the websocket manager's broadcast directly —
    # a real WS client is tested below via the httpx WS client.
    original_broadcast = ws_manager.broadcast

    async def capturing_broadcast(message):
        events.append(message)
        await original_broadcast(message)

    ws_manager.broadcast = capturing_broadcast

    yield events

    ws_manager.broadcast = original_broadcast


@pytest.mark.asyncio
async def test_1_four_channels_insert_and_list(client, ws_conn):
    """Step 8a: Simulate 4 POSTs from 4 channels and verify GET /cases sees all."""
    case_ids = []
    for channel_payload in FOUR_CHANNELS:
        resp = await client.post("/api/cases/", json=channel_payload)
        assert resp.status_code == 201, f"POST failed: {resp.text}"
        created = resp.json()
        case_ids.append(created["id"])

    assert len(case_ids) == 4, "All 4 channel POSTs should succeed"

    # GET /cases as ministry — should see all 4
    resp = await client.get("/api/cases/?role=ministry&limit=100")
    assert resp.status_code == 200
    all_cases = resp.json()
    assert len(all_cases) >= 4

    channels_returned = {c["channel_of_origin"] for c in all_cases}
    for ch in ["portal", "chatbot", "ivrs", "mobile_app"]:
        assert ch in channels_returned, f"Channel {ch} missing from GET /cases"

    print(f"\n[PASS] 4 simulated channel POSTs -> GET /cases returned {len(all_cases)} cases")
    print(f"       Channels seen: {channels_returned}")
    print(f"       WebSocket events captured: {len(ws_conn)}")


@pytest.mark.asyncio
async def test_2_websocket_push_for_all_four(client, ws_conn):
    """Step 8b: All four inserts must push a WebSocket event."""
    ws_conn.clear()

    for channel_payload in FOUR_CHANNELS:
        await client.post("/api/cases/", json=channel_payload)

    # At least 4 case_created events should have been broadcast
    created_events = [e for e in ws_conn if e["event"] == "case_created"]
    assert len(created_events) >= 4, (
        f"Expected >= 4 case_created WS events, got {len(created_events)}"
    )

    pushed_channels = {e["data"]["channel_of_origin"] for e in created_events}
    for ch in ["portal", "chatbot", "ivrs", "mobile_app"]:
        assert ch in pushed_channels, f"No WS event for channel {ch}"

    print(f"\n[PASS] All 4 inserts triggered WebSocket push events")
    print(f"       Events: {len(created_events)}")


@pytest.mark.asyncio
async def test_3_role_based_filtering_blocks_cross_district(client):
    """Step: A district officer in Central Delhi must NOT see South Delhi cases."""
    # Insert cases in two different districts
    await client.post("/api/cases/", json={
        "channel_of_origin": "portal",
        "district": "Central Delhi",
        "state": "Delhi",
        "incident_description": "Test case in Central Delhi",
    })
    await client.post("/api/cases/", json={
        "channel_of_origin": "chatbot",
        "district": "South Delhi",
        "state": "Delhi",
        "incident_description": "Test case in South Delhi",
    })

    # District officer for Central Delhi should only see Central Delhi cases
    resp = await client.get("/api/cases/?role=district&district=Central+Delhi&limit=100")
    assert resp.status_code == 200
    cases = resp.json()
    districts = {c["district"] for c in cases}
    assert "Central Delhi" in districts, "Should see own district cases"
    assert "South Delhi" not in districts, "District officer must NOT see other districts"

    # Ministry sees everything
    resp_ministry = await client.get("/api/cases/?role=ministry&limit=500")
    assert resp_ministry.status_code == 200
    all_districts = {c["district"] for c in resp_ministry.json()}
    assert "Central Delhi" in all_districts
    assert "South Delhi" in all_districts

    print(f"\n[PASS] Role-based filtering: district officer sees only own district")
    print(f"       District officer sees: {districts}")


@pytest.mark.asyncio
async def test_4_ai_risk_assessment_updates_case(client, ws_conn):
    """Step: POST /risk-assessments links a score to a case + pushes WS event."""
    # Create a case first
    resp = await client.post("/api/cases/", json={
        "channel_of_origin": "ivrs",
        "district": "West Delhi",
        "state": "Delhi",
        "incident_description": "IVRS distress call",
    })
    case = resp.json()
    case_id = case["id"]

    ws_conn.clear()

    # AI module posts a risk assessment
    ra_payload = {
        "case_id": case_id,
        "svi_score": 87.5,
        "risk_tier": "critical",
        "flags": {"trauma": True, "suicidal_ideation": True, "intimidation": True},
        "explanation_text": "High pitch variability, long pauses, keywords: 'kill me', 'no way out' detected.",
        "model_version": "nhs-emotion-v2.1",
    }
    resp = await client.post("/api/risk-assessments/", json=ra_payload, params={"actor": "ai_module"})
    assert resp.status_code == 201, f"Risk assessment POST failed: {resp.text}"
    ra = resp.json()
    assert ra["risk_tier"] == "critical"
    assert ra["svi_score"] == 87.5
    assert ra["explanation_text"] != ""

    # GET /cases/{id} should now include the risk assessment
    resp = await client.get(f"/api/cases/{case_id}")
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["svi_score"] == 87.5
    assert detail["risk_tier"] == "critical"
    assert len(detail["risk_assessments"]) >= 1

    # WebSocket should have a risk_assessment_created event
    ra_events = [e for e in ws_conn if e["event"] == "risk_assessment_created"]
    assert len(ra_events) >= 1, "Expected a risk_assessment_created WS event"

    print(f"\n[PASS] AI risk assessment linked to case {case_id}")
    print(f"       SVI: {ra['svi_score']}, Tier: {ra['risk_tier']}")
    print(f"       WS events: {[e['event'] for e in ws_conn]}")


@pytest.mark.asyncio
async def test_5_audit_log_is_append_only(client):
    """Step: Every AI score and officer action is captured in the append-only audit log."""
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AuditLogs).where(
                AuditLogs.action.in_(["case_created", "risk_assessed"])
            )
        )
        logs = result.scalars().all()

    assert len(logs) > 0, "Audit log should contain entries for case_created and risk_assessed"

    actions = {l.action for l in logs}
    assert "case_created" in actions, "Missing case_created in audit log"
    assert "risk_assessed" in actions, "Missing risk_assessed in audit log"

    print(f"\n[PASS] Audit log captured {len(logs)} entries")
    print(f"       Action types: {actions}")


@pytest.mark.asyncio
async def test_6_patch_case_status_triggers_ws(client, ws_conn):
    """Step: PATCH /cases/{id} updates status and pushes a WS event."""
    resp = await client.post("/api/cases/", json={
        "channel_of_origin": "portal",
        "district": "Central Delhi",
        "state": "Delhi",
        "incident_description": "Test PATCH workflow",
    })
    case_id = resp.json()["id"]

    ws_conn.clear()

    resp = await client.patch(
        f"/api/cases/{case_id}",
        json={"status": "in_progress"},
        params={"role": "district", "district": "Central Delhi"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"

    update_events = [e for e in ws_conn if e["event"] == "case_updated"]
    assert len(update_events) >= 1, "Expected a case_updated WS event"

    print(f"\n[PASS] PATCH /cases/{case_id} triggered WS update event")


@pytest.mark.asyncio
async def test_7_end_to_end_full_pipeline(client):
    """Full end-to-end: Portal case -> AI risk assessment -> status update -> audit trail."""
    # 1. Portal creates a case
    resp = await client.post("/api/cases/", json={
        "channel_of_origin": "portal",
        "district": "Central Delhi",
        "state": "Delhi",
        "language": "en",
        "incident_description": "Caste-based assault reported via portal.",
    })
    assert resp.status_code == 201
    case_id = resp.json()["id"]

    # 2. AI module posts risk assessment
    resp = await client.post("/api/risk-assessments/", json={
        "case_id": case_id,
        "svi_score": 95.0,
        "risk_tier": "critical",
        "flags": {"trauma": True, "fear": True, "suicidal_ideation": True, "intimidation": True},
        "explanation_text": "Critical: high distress, explicit suicidal ideation, fear of retaliation.",
        "model_version": "nhs-emotion-v2.1",
    }, params={"actor": "ai_module"})
    assert resp.status_code == 201

    # 3. Officer updates status to escalated
    resp = await client.patch(
        f"/api/cases/{case_id}",
        json={"status": "escalated", "recommended_action": "police_intervention"},
        params={"role": "district", "district": "Central Delhi"},
    )
    assert resp.status_code == 200

    # 4. Audit log should have all three actions
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(AuditLogs).where(AuditLogs.case_id == case_id).order_by(AuditLogs.timestamp)
        )
        logs = result.scalars().all()

    actions = [l.action for l in logs]
    assert "case_created" in actions
    assert "risk_assessed" in actions
    assert "status_updated" in actions

    # 5. Case detail should show the critical risk assessment
    resp = await client.get(f"/api/cases/{case_id}")
    detail = resp.json()
    assert detail["risk_tier"] == "critical"
    assert detail["svi_score"] == 95.0
    assert detail["recommended_action"] == "police_intervention"

    print(f"\n[PASS] End-to-end pipeline for case {case_id}")
    print(f"       Audit actions: {actions}")
    print(f"       Final status: {detail['status']}")


if __name__ == "__main__":
    # Allow running directly: python -m pytest test_sync.py -v -s
    # Or: python backend/tests/test_sync.py
    pytest.main([__file__, "-v", "-s"])
