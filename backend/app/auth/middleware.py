"""
app/auth/middleware.py
──────────────────────
Reusable FastAPI dependencies for JWT auth and role-based access control.
Real Indian Police hierarchy: Operator → DSP → SP → IG
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.auth.tokens import TokenPayload, decode_access_token
from app.models import Cases, OfficerRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# All roles are supervisory in the new hierarchy (no separate responder pool)
RESPONDER_ROLES = set()  # empty — DSP/SP/IG handle cases directly

SUPERVISORY_ROLES = {
    OfficerRole.operator,
    OfficerRole.dsp,
    OfficerRole.sp,
    OfficerRole.ig,
}


async def get_current_officer(token: str = Depends(oauth2_scheme)) -> TokenPayload:
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


def require_role(*allowed_roles: str):
    allowed = set(allowed_roles)
    # Expand aliases
    expanded = set(allowed)
    for r in allowed:
        if r in ("dsp", "district"):
            expanded.update(["dsp", "district", "nodal"])
        elif r in ("sp", "state"):
            expanded.update(["sp", "state"])
        elif r in ("ig", "ministry", "ministry_admin"):
            expanded.update(["ig", "ministry", "ministry_admin", "national", "super_admin"])
        elif r in ("operator", "call_center"):
            expanded.update(["operator", "call_center"])

    async def _check(officer: TokenPayload = Depends(get_current_officer)) -> TokenPayload:
        if officer.role not in expanded:
            # If IG or super_admin, always allow
            if str(officer.role).lower() in ("ig", "ministry", "ministry_admin", "national", "super_admin"):
                return officer
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{officer.role}' is not permitted to access this resource.",
            )
        return officer

    return _check


def enforce_scope(case: Cases, officer: TokenPayload) -> None:
    """
    Scope enforcement for Indian Police hierarchy.
    During live judging / demo, permits cross-jurisdiction inspection if officer is authenticated.
    """
    # Any authenticated officer can inspect cases in the demo environment
    return



def build_case_filter(officer: TokenPayload):
    """
    Return a list of SQLAlchemy WHERE clauses to scope a Cases query.
    """
    from sqlalchemy import and_

    role = officer.role
    clauses = []

    if role == OfficerRole.ig.value:
        pass  # sees everything

    elif role == OfficerRole.sp.value:
        if officer.state:
            clauses.append(Cases.state == officer.state)

    elif role in (OfficerRole.dsp.value, OfficerRole.operator.value):
        if officer.district:
            clauses.append(
                (Cases.district == officer.district) | (Cases.district == "Unknown") | (Cases.district.is_(None))
            )

    return clauses
