"""
seed_test_officers.py
─────────────────────
Creates one test officer account per role (8 total) so that Pawan, Pushp,
and Vinit can immediately test all access levels.

Run from the backend/ directory:
    python seed_test_officers.py

The script is idempotent — if a username already exists it will be skipped.

Test credentials (all passwords: Test@1234):
┌────────────────────────┬──────────────────────┬──────────────┬─────────────────┐
│ Username               │ Role                 │ District     │ State           │
├────────────────────────┼──────────────────────┼──────────────┼─────────────────┤
│ op_delhi_01            │ operator             │ Central Delhi│ Delhi           │
│ dist_delhi_01          │ district             │ Central Delhi│ Delhi           │
│ state_delhi_01         │ state                │ —            │ Delhi           │
│ ministry_01            │ ministry             │ —            │ —               │
│ police_delhi_01        │ police               │ Central Delhi│ Delhi           │
│ dlsa_delhi_01          │ dlsa                 │ Central Delhi│ Delhi           │
│ medical_delhi_01       │ medical              │ Central Delhi│ Delhi           │
│ counselor_delhi_01     │ counselor            │ Central Delhi│ Delhi           │
└────────────────────────┴──────────────────────┴──────────────┴─────────────────┘
"""

import asyncio
import sys
import os

# Allow running from the backend/ directory without installing the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.database import AsyncSessionLocal, engine, Base
from app.models import Officers, OfficerRole
from app.auth.hashing import hash_password

DEFAULT_PASSWORD = "Test@1234"

TEST_OFFICERS = [
    {
        "name": "Priya Sharma",
        "username": "operator",
        "role": OfficerRole.operator,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "OPR-000",
    },
    {
        "name": "Ravi Kumar (Operator)",
        "username": "op_delhi_01",
        "role": OfficerRole.operator,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "OPR-001",
    },
    {
        "name": "Sunita Sharma (District Officer)",
        "username": "dist_delhi_01",
        "role": OfficerRole.district,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "DST-001",
    },
    {
        "name": "Anand Singh (State Officer)",
        "username": "state_delhi_01",
        "role": OfficerRole.state,
        "district": None,
        "state": "Delhi",
        "badge_id": "ST-001",
    },
    {
        "name": "Priya Mehta (Ministry Admin)",
        "username": "ministry_01",
        "role": OfficerRole.ministry,
        "district": None,
        "state": None,
        "badge_id": "MIN-001",
    },
    {
        "name": "Inspector Ramesh (Police)",
        "username": "police_delhi_01",
        "role": OfficerRole.police,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "POL-001",
    },
    {
        "name": "Inspector Ramesh (Police)",
        "username": "police",
        "role": OfficerRole.police,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "POL-000",
    },
    {
        "name": "Advocate Neha Gupta (DLSA)",
        "username": "dlsa_delhi_01",
        "role": OfficerRole.dlsa,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "DLSA-001",
    },
    {
        "name": "Advocate Neha Gupta (DLSA)",
        "username": "dlsa",
        "role": OfficerRole.dlsa,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "DLSA-000",
    },
    {
        "name": "Dr. Kavita Rao (Medical)",
        "username": "medical_delhi_01",
        "role": OfficerRole.medical,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "MED-001",
    },
    {
        "name": "Dr. Kavita Rao (Medical)",
        "username": "medical",
        "role": OfficerRole.medical,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "MED-000",
    },
    {
        "name": "Counselor Deepa Nair",
        "username": "counselor_delhi_01",
        "role": OfficerRole.counselor,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "CNS-001",
    },
    {
        "name": "Counselor Deepa Nair",
        "username": "counselor",
        "role": OfficerRole.counselor,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "CNS-000",
    },
    {
        "name": "Major Vikram (Witness Protection)",
        "username": "witness_protection",
        "role": OfficerRole.witness_protection,
        "district": "Central Delhi",
        "state": "Delhi",
        "badge_id": "WP-001",
    },
]


async def seed():
    # Ensure all tables exist (safe to call on an existing DB)
    import app.models  # noqa: F401 — register models

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    hashed_pw = hash_password(DEFAULT_PASSWORD)
    created = 0
    skipped = 0

    async with AsyncSessionLocal() as db:
        for data in TEST_OFFICERS:
            # Check if username already exists
            result = await db.execute(
                select(Officers).where(Officers.username == data["username"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"  [SKIP]  {data['username']} (already exists, id={existing.id})")
                skipped += 1
                continue

            officer = Officers(
                name=data["name"],
                username=data["username"],
                password_hash=hashed_pw,
                role=data["role"],
                district=data["district"],
                state=data["state"],
                badge_id=data["badge_id"],
                is_active=True,
            )
            db.add(officer)
            await db.flush()  # get the id before commit
            print(f"  [OK]  CREATE {data['username']}  role={data['role'].value}  id={officer.id}")
            created += 1

        await db.commit()

    print(f"\nDone — {created} created, {skipped} skipped.")
    print(f"All accounts use password: {DEFAULT_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
