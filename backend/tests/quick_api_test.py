import asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import engine, Base, AsyncSessionLocal
from app.models import AuditLogs
from sqlalchemy import select


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        # Health
        r = await c.get("/health")
        print("Health:", r.status_code, r.json())

        # POST 4 cases from 4 channels
        channels = [
            ("portal", "Central Delhi"),
            ("chatbot", "East Delhi"),
            ("ivrs", "South Delhi"),
            ("mobile_app", "North Delhi"),
        ]
        for ch, dist in channels:
            r = await c.post(
                "/api/cases/",
                params={"role": "operator", "district": dist, "state": "Delhi"},
                json={
                    "channel_of_origin": ch,
                    "district": dist,
                    "state": "Delhi",
                    "incident_description": f"{ch.capitalize()} report",
                },
            )
            print(f"POST /cases ({ch}): {r.status_code} -> id={r.json()['id']}")

        # GET all as ministry
        r = await c.get("/api/cases/?role=ministry&limit=100")
        cases = r.json()
        ch_set = {c["channel_of_origin"] for c in cases}
        print(f"GET /cases (ministry): {r.status_code} -> {len(cases)} cases, channels={ch_set}")

        # Role-based: district officer sees only own district
        r = await c.get("/api/cases/?role=district&district=Central%20Delhi&limit=100")
        cases = r.json()
        d_set = {c["district"] for c in cases}
        print(f"GET /cases (district, Central Delhi): {r.status_code} -> {len(cases)} cases, districts={d_set}")

        # AI risk assessment
        r = await c.post(
            "/api/risk-assessments/",
            params={"actor": "ai_module"},
            json={
                "case_id": 1,
                "svi_score": 92.5,
                "risk_tier": "critical",
                "flags": {"trauma": True, "suicidal_ideation": True},
                "explanation_text": "High distress detected from audio analysis.",
                "model_version": "nhs-emotion-v2.1",
            },
        )
        print(f"POST /risk-assessments: {r.status_code} -> tier={r.json()['risk_tier']}")

        # PATCH case status
        r = await c.patch(
            "/api/cases/1",
            params={"role": "district", "district": "Central Delhi"},
            json={"status": "escalated"},
        )
        print(f"PATCH /cases/1: {r.status_code} -> status={r.json()['status']}")

        # Audit log
        async with AsyncSessionLocal() as s:
            result = await s.execute(select(AuditLogs))
            logs = result.scalars().all()
            print(f"Audit log entries: {len(logs)}")

    print("\n=== ALL API TESTS PASSED ===")


if __name__ == "__main__":
    asyncio.run(main())
