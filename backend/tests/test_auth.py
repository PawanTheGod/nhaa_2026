"""
tests/test_auth.py
──────────────────
Automated test suite for Aditya's Auth, RBAC, and Admin Panel API Layer.

Tests:
  1. POST /auth/login (success & failure)
  2. Audit log entry generation on login attempts
  3. GET /auth/me profile rehydration
  4. Role-based access control (RBAC) on supervisory stats endpoints (403 vs 200)
  5. Scoped case retrieval (Operator/District/State/Ministry)
  6. Strict Responder isolation (Police vs DLSA vs Medical)
  7. SLA monitoring endpoint role gating
  8. POST /api/officer-decision override & audit verification
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.auth.hashing import hash_password
from app.database import AsyncSessionLocal, Base, engine
from app.main import app
from app.models import (
    AuditLogs,
    Cases,
    CaseStatus,
    ChannelOrigin,
    OfficerRole,
    Officers,
    RiskAssessments,
    RiskTier,
    SlaDeadlines,
)
from datetime import datetime, timezone, timedelta


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed test officers
    async with AsyncSessionLocal() as db:
        pw_hash = hash_password("Test@1234")
        officers_data = [
            Officers(
                id=1,
                name="Ravi Kumar (Operator)",
                username="op_delhi_01",
                password_hash=pw_hash,
                role=OfficerRole.operator,
                district="Central Delhi",
                state="Delhi",
                badge_id="OPR-001",
                is_active=True,
            ),
            Officers(
                id=9,
                name="Priya Sharma",
                username="operator",
                password_hash=pw_hash,
                role=OfficerRole.operator,
                district="Central Delhi",
                state="Delhi",
                badge_id="OPR-000",
                is_active=True,
            ),
            Officers(
                id=2,
                name="Sunita Sharma (District)",
                username="dist_delhi_01",
                password_hash=pw_hash,
                role=OfficerRole.district,
                district="Central Delhi",
                state="Delhi",
                badge_id="DST-001",
                is_active=True,
            ),
            Officers(
                id=3,
                name="Anand Singh (State)",
                username="state_delhi_01",
                password_hash=pw_hash,
                role=OfficerRole.state,
                district=None,
                state="Delhi",
                badge_id="ST-001",
                is_active=True,
            ),
            Officers(
                id=4,
                name="Priya Mehta (Ministry)",
                username="ministry_01",
                password_hash=pw_hash,
                role=OfficerRole.ministry,
                district=None,
                state=None,
                badge_id="MIN-001",
                is_active=True,
            ),
            Officers(
                id=5,
                name="Inspector Ramesh (Police)",
                username="police_delhi_01",
                password_hash=pw_hash,
                role=OfficerRole.police,
                district="Central Delhi",
                state="Delhi",
                badge_id="POL-001",
                is_active=True,
            ),
            Officers(
                id=10,
                name="Inspector Ramesh (Police)",
                username="police",
                password_hash=pw_hash,
                role=OfficerRole.police,
                district="Central Delhi",
                state="Delhi",
                badge_id="POL-000",
                is_active=True,
            ),
            Officers(
                id=6,
                name="Advocate Neha (DLSA)",
                username="dlsa_delhi_01",
                password_hash=pw_hash,
                role=OfficerRole.dlsa,
                district="Central Delhi",
                state="Delhi",
                badge_id="DLSA-001",
                is_active=True,
            ),
        ]
        for off in officers_data:
            db.add(off)

        # Seed sample test cases
        # Case 1: Central Delhi, assigned to Police (Officer 5)
        c1 = Cases(
            id=101,
            channel_of_origin=ChannelOrigin.ivrs,
            district="Central Delhi",
            state="Delhi",
            status=CaseStatus.in_progress,
            risk_tier=RiskTier.high,
            svi_score=78.5,
            recommended_action="immediate_police_response",
            assigned_officer_id=5,
            incident_description="Distress call received via IVRS helpline.",
        )
        # Case 2: South Delhi (outside Central Delhi), assigned to DLSA (Officer 6)
        c2 = Cases(
            id=102,
            channel_of_origin=ChannelOrigin.chatbot,
            district="South Delhi",
            state="Delhi",
            status=CaseStatus.new,
            risk_tier=RiskTier.moderate,
            svi_score=45.0,
            recommended_action="legal_aid_consultation",
            assigned_officer_id=6,
            incident_description="Legal assistance requested via chatbot.",
        )
        # Case 3: Mumbai, Maharashtra
        c3 = Cases(
            id=103,
            channel_of_origin=ChannelOrigin.portal,
            district="Mumbai City",
            state="Maharashtra",
            status=CaseStatus.resolved,
            risk_tier=RiskTier.low,
            svi_score=20.0,
            incident_description="General enquiry through portal.",
        )
        db.add_all([c1, c2, c3])

        # SLA deadline for Case 101
        sla = SlaDeadlines(
            id=1,
            case_id=101,
            deadline_type="first_response",
            due_date=datetime.now(timezone.utc) + timedelta(hours=4),
            met=False,
        )
        db.add(sla)

        await db.commit()

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_auth_login_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/auth/login",
            data={"username": "op_delhi_01", "password": "Test@1234"},
        )
        assert res.status_code == 200
        body = res.json()
        assert "access_token" in body
        assert body["officer"]["username"] if "username" in body["officer"] else body["officer"]["role"] == "operator"
        assert body["officer"]["district"] == "Central Delhi"


@pytest.mark.asyncio
async def test_auth_login_failure_and_audit():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/auth/login",
            data={"username": "op_delhi_01", "password": "WrongPassword"},
        )
        assert res.status_code == 401

        # Check audit log for login_failure
        async with AsyncSessionLocal() as db:
            audit = await db.execute(
                select(AuditLogs).where(
                    AuditLogs.actor == "op_delhi_01",
                    AuditLogs.action == "login_failure"
                )
            )
            entry = audit.scalar_one_or_none()
            assert entry is not None


@pytest.mark.asyncio
async def test_auth_me_profile():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login
        login_res = await client.post(
            "/auth/login",
            data={"username": "dist_delhi_01", "password": "Test@1234"},
        )
        token = login_res.json()["access_token"]

        # Call /auth/me
        me_res = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_res.status_code == 200
        me = me_res.json()
        assert me["name"] == "Sunita Sharma (District)"
        assert me["role"] == "district"


@pytest.mark.asyncio
async def test_national_stats_role_gate():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Operator login -> should get 403 on national stats
        op_login = await client.post(
            "/auth/login",
            data={"username": "op_delhi_01", "password": "Test@1234"},
        )
        op_token = op_login.json()["access_token"]
        op_stats = await client.get(
            "/api/stats/national",
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert op_stats.status_code == 403

        # Ministry login -> should get 200
        min_login = await client.post(
            "/auth/login",
            data={"username": "ministry_01", "password": "Test@1234"},
        )
        min_token = min_login.json()["access_token"]
        min_stats = await client.get(
            "/api/stats/national",
            headers={"Authorization": f"Bearer {min_token}"},
        )
        assert min_stats.status_code == 200
        assert min_stats.json()["total_cases"] == 3


@pytest.mark.asyncio
async def test_cases_scope_and_responder_isolation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Operator (Central Delhi) sees only Case 101
        op_login = await client.post(
            "/auth/login",
            data={"username": "op_delhi_01", "password": "Test@1234"},
        )
        op_token = op_login.json()["access_token"]
        res = await client.get("/api/cases", headers={"Authorization": f"Bearer {op_token}"})
        assert res.status_code == 200
        cases = res.json()
        case_ids = [c["id"] for c in cases]
        assert 101 in case_ids
        assert 102 not in case_ids
        assert 103 not in case_ids

        # 2. State Officer (Delhi) sees Case 101 and 102 (both Delhi), but not 103 (Maharashtra)
        st_login = await client.post(
            "/auth/login",
            data={"username": "state_delhi_01", "password": "Test@1234"},
        )
        st_token = st_login.json()["access_token"]
        res = await client.get("/api/cases", headers={"Authorization": f"Bearer {st_token}"})
        assert res.status_code == 200
        st_case_ids = [c["id"] for c in res.json()]
        assert 101 in st_case_ids
        assert 102 in st_case_ids
        assert 103 not in st_case_ids

        # 3. Ministry Officer sees ALL 3 cases
        min_login = await client.post(
            "/auth/login",
            data={"username": "ministry_01", "password": "Test@1234"},
        )
        min_token = min_login.json()["access_token"]
        res = await client.get("/api/cases", headers={"Authorization": f"Bearer {min_token}"})
        assert res.status_code == 200
        assert len(res.json()) == 3

        # 4. Police Officer (Officer ID 5) sees ONLY Case 101 (assigned to 5)
        pol_login = await client.post(
            "/auth/login",
            data={"username": "police_delhi_01", "password": "Test@1234"},
        )
        pol_token = pol_login.json()["access_token"]
        res = await client.get("/api/cases", headers={"Authorization": f"Bearer {pol_token}"})
        assert res.status_code == 200
        pol_cases = res.json()
        assert len(pol_cases) == 1
        assert pol_cases[0]["id"] == 101

        # 5. DLSA Officer (Officer ID 6) sees ONLY Case 102 (assigned to 6), NEVER Case 101 (Police)
        dlsa_login = await client.post(
            "/auth/login",
            data={"username": "dlsa_delhi_01", "password": "Test@1234"},
        )
        dlsa_token = dlsa_login.json()["access_token"]
        res = await client.get("/api/cases", headers={"Authorization": f"Bearer {dlsa_token}"})
        assert res.status_code == 200
        dlsa_cases = res.json()
        assert len(dlsa_cases) == 1
        assert dlsa_cases[0]["id"] == 102

        # 6. DLSA Officer directly requesting Police's Case 101 -> 403 Forbidden
        dlsa_detail = await client.get(
            "/api/cases/101",
            headers={"Authorization": f"Bearer {dlsa_token}"},
        )
        assert dlsa_detail.status_code == 403


@pytest.mark.asyncio
async def test_sla_status_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Operator can check SLA
        op_login = await client.post(
            "/auth/login",
            data={"username": "op_delhi_01", "password": "Test@1234"},
        )
        op_token = op_login.json()["access_token"]
        sla_res = await client.get("/api/sla-status", headers={"Authorization": f"Bearer {op_token}"})
        assert sla_res.status_code == 200
        data = sla_res.json()
        assert len(data) > 0
        assert data[0]["case_id"] == 101

        # Responder cannot check supervisory SLA status -> 403
        pol_login = await client.post(
            "/auth/login",
            data={"username": "police_delhi_01", "password": "Test@1234"},
        )
        pol_token = pol_login.json()["access_token"]
        pol_sla = await client.get("/api/sla-status", headers={"Authorization": f"Bearer {pol_token}"})
        assert pol_sla.status_code == 403


@pytest.mark.asyncio
async def test_officer_decision_and_override():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        op_login = await client.post(
            "/auth/login",
            data={"username": "op_delhi_01", "password": "Test@1234"},
        )
        op_token = op_login.json()["access_token"]

        decision_payload = {
            "case_id": 101,
            "decision_type": "override",
            "category": "domestic_violence",
            "override_risk_tier": "critical",
            "notes": "Escalated by operator after victim distress call.",
        }
        res = await client.post(
            "/api/officer-decision",
            json=decision_payload,
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["recorded"] is True
        assert data["consistency_check_triggered"] is True
        assert "audit_id" in data

        # Verify case tier was updated to critical
        detail = await client.get("/api/cases/101", headers={"Authorization": f"Bearer {op_token}"})
        assert detail.json()["risk_tier"] == "critical"


@pytest.mark.asyncio
async def test_json_login_pawan_contract():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # JSON login per Pawan's contract
        res = await client.post(
            "/auth/login",
            json={"username": "operator", "password": "Test@1234"},
        )
        assert res.status_code == 200
        body = res.json()
        assert "token" in body
        assert body["role"] == "operator"
        assert body["name"] == "Priya Sharma"
        assert body["district"] == "Central Delhi"
        assert body["state"] == "Delhi"


@pytest.mark.asyncio
async def test_critical_confirm_and_responder_actioned():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Operator confirms critical dispatch
        op_login = await client.post(
            "/auth/login",
            json={"username": "operator", "password": "Test@1234"},
        )
        op_token = op_login.json()["token"]

        confirm_res = await client.post(
            "/api/decisions/confirm",
            json={
                "case_id": 101,
                "action": "confirm_critical_dispatch",
                "officer_id": "operator",
            },
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert confirm_res.status_code == 200
        confirm_body = confirm_res.json()
        assert confirm_body["confirmed"] is True
        assert confirm_body["case_id"] == 101

        # 2. Police marks task as actioned (Officer 5, who is assigned to Case 101)
        pol_login = await client.post(
            "/auth/login",
            json={"username": "police_delhi_01", "password": "Test@1234"},
        )
        pol_token = pol_login.json()["token"]

        act_res = await client.patch(
            "/api/decisions/101/actioned",
            json={"responder_type": "police", "actioned": True},
            headers={"Authorization": f"Bearer {pol_token}"},
        )
        assert act_res.status_code == 200
        act_body = act_res.json()
        assert act_body["case_id"] == 101
        assert act_body["actioned"] is True


@pytest.mark.asyncio
async def test_action_and_full_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Operator logs in and escalates Case 102 (if operator had scope for South Delhi)
        # Wait, op_delhi_01 is Central Delhi, Case 102 is South Delhi. They get 403 on 102.
        # Let's escalate Case 101
        op_login = await client.post(
            "/auth/login",
            json={"username": "op_delhi_01", "password": "Test@1234"},
        )
        op_token = op_login.json()["access_token"]

        # Check allowed actions
        allowed = await client.get(
            "/api/cases/101/allowed-actions",
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert allowed.status_code == 200
        assert "escalate" in allowed.json()["allowed_actions"]

        # Take escalate action
        action_res = await client.post(
            "/api/cases/101/action",
            json={"action": "escalate", "notes": "Escalating case"},
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert action_res.status_code == 200
        assert action_res.json()["status"] == "escalated"

        # Check full case detail
        full_res = await client.get(
            "/api/cases/101/full",
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert full_res.status_code == 200
        full_data = full_res.json()
        assert "history" in full_data
        assert any(h["action"] == "case_action_escalate" for h in full_data["history"])

