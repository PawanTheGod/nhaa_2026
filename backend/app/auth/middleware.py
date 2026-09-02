"""
app/auth/middleware.py
──────────────────────
Reusable FastAPI dependencies for JWT auth and role-based access control.

Usage in a route:
    from app.auth.middleware import get_current_officer, require_role, enforce_scope

    @router.get("/api/cases")
    async def list_cases(
        officer: TokenPayload = Depends(get_current_officer),
        db: AsyncSession = Depends(get_db),
    ):
        ...

    # Restrict to specific roles:
    @router.get("/api/stats/national")
    async def national_stats(
        officer: TokenPayload = Depends(require_role("ministry")),
    ):
        ...
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.auth.tokens import TokenPayload, decode_access_token
from app.models import Cases, OfficerRole

# Tells FastAPI/Swagger where to obtain a token (for the Authorize button)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ── Roles that are "responders" (not supervisory hierarchy) ──────────────────
RESPONDER_ROLES = {
    OfficerRole.police,
    OfficerRole.dlsa,
    OfficerRole.medical,
    OfficerRole.counselor,
    OfficerRole.witness_protection,
}

SUPERVISORY_ROLES = {
    OfficerRole.operator,
    OfficerRole.district,
    OfficerRole.state,
    OfficerRole.ministry,
}


# ── Core dependency ───────────────────────────────────────────────────────────

async def get_current_officer(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    """
    Dependency: extract and verify the Bearer JWT from the incoming request.

    Returns the decoded TokenPayload on success.
    Raises HTTP 401 if token is missing, malformed, or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise credentials_exception
    return payload


# ── Role gate factory ─────────────────────────────────────────────────────────

def require_role(*allowed_roles: str):
    """
    Factory that returns a FastAPI dependency enforcing one of *allowed_roles*.

    Example:
        Depends(require_role("ministry"))
        Depends(require_role("district", "state", "ministry"))
    """
    allowed = set(allowed_roles)

    async def _check(officer: TokenPayload = Depends(get_current_officer)) -> TokenPayload:
        if officer.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{officer.role}' is not permitted to access this resource.",
            )
        return officer

    return _check


# ── Data-scope enforcement ────────────────────────────────────────────────────

def enforce_scope(case: Cases, officer: TokenPayload) -> None:
    """
    Raise HTTP 403 if *officer* is not allowed to view *case*.

    Rules:
    - ministry  → sees everything
    - state     → must match case.state
    - district  → must match case.district
    - operator  → must match case.district  (operators work within their district)
    - responders → must be the assigned_officer on the case
                   (police only sees their own; dlsa only sees their own, etc.)
    """
    role = officer.role

    if role == OfficerRole.ministry.value:
        return  # no restriction

    if role == OfficerRole.state.value:
        if officer.state and case.state != officer.state:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Case is outside your state.",
            )
        return

    if role in (OfficerRole.district.value, OfficerRole.operator.value):
        if officer.district and case.district != officer.district:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Case is outside your district.",
            )
        return

    # Responder roles: must be the assigned officer
    if role in {r.value for r in RESPONDER_ROLES}:
        if case.assigned_officer_id is None or str(case.assigned_officer_id) != officer.sub:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This case is not assigned to you.",
            )
        return

    # Unknown role — deny by default
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied.",
    )


def build_case_filter(officer: TokenPayload):
    """
    Return a list of SQLAlchemy WHERE clauses to scope a Cases query
    to what *officer* is allowed to see.

    Designed to be spread into .where(*build_case_filter(officer)).
    """
    from sqlalchemy import and_

    role = officer.role
    clauses = []

    if role == OfficerRole.ministry.value:
        pass  # sees everything — no additional filter

    elif role == OfficerRole.state.value:
        if officer.state:
            clauses.append(Cases.state == officer.state)

    elif role in (OfficerRole.district.value, OfficerRole.operator.value):
        if officer.district:
            clauses.append(Cases.district == officer.district)

    elif role in {r.value for r in RESPONDER_ROLES}:
        # Responders see ONLY cases assigned to them
        clauses.append(Cases.assigned_officer_id == int(officer.sub))

    return clauses
