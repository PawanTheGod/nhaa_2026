"""
app/routes/auth.py
──────────────────
Authentication endpoints for the NHAA Admin Panel.

Endpoints:
    POST /auth/login   – issue a signed JWT, log attempt to audit_logs
    POST /auth/logout  – stateless logout (logs to audit_logs)
    GET  /auth/me      – return current officer profile from token
                         (useful for Pawan's screens to rehydrate state on page refresh)
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.hashing import verify_password
from app.auth.middleware import get_current_officer
from app.auth.tokens import TokenPayload, create_access_token
from app.database import AsyncSessionLocal
from app.models import Officers
from app.routes.audit import log_action

router = APIRouter(prefix="/auth", tags=["auth"])


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── Response schemas ──────────────────────────────────────────────────────────

class OfficerProfile(BaseModel):
    id: int
    name: str
    role: str
    district: str | None
    state: str | None
    badge_id: str | None


class LoginIn(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str
    district: str | None = None
    state: str | None = None
    officer_id: int
    officer: OfficerProfile


# ── POST /auth/login ──────────────────────────────────────────────────────────

from fastapi import Request

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Officer login — returns a signed JWT",
    description=(
        "Accepts either JSON `{ \"username\": \"...\", \"password\": \"...\" }` "
        "or OAuth2 form-encoded data. "
        "Returns signed JWT containing `role`, `name`, `district`, `state` claims."
    ),
)
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handles both JSON bodies (from Pawan's React login screen)
    and Form data (from Swagger Authorize UI).
    """
    username = ""
    password = ""

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            username = body.get("username", "").strip()
            password = body.get("password", "")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body",
            )
    else:
        # Fallback to form data
        form = await request.form()
        username = form.get("username", "").strip()
        password = form.get("password", "")

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )

    result = await db.execute(
        select(Officers).where(Officers.username == username)
    )
    officer = result.scalar_one_or_none()

    # ── Authenticate ──────────────────────────────────────────────────────────
    auth_ok = (
        officer is not None
        and officer.is_active
        and officer.password_hash is not None
        and verify_password(password, officer.password_hash)
    )

    # ── Audit log (always, win or lose) ──────────────────────────────────────
    await log_action(
        db,
        actor=username,
        action="login_success" if auth_ok else "login_failure",
        case_id=None,
        details={
            "role": officer.role.value if officer else None,
            "district": officer.district if officer else None,
            "state": officer.state if officer else None,
            "ip": request.client.host if request.client else "n/a",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    if not auth_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        officer_id=officer.id,
        role=officer.role.value,
        name=officer.name,
        district=officer.district,
        state=officer.state,
    )

    return LoginResponse(
        token=token,
        access_token=token,
        token_type="bearer",
        role=officer.role.value,
        name=officer.name,
        district=officer.district,
        state=officer.state,
        officer_id=officer.id,
        officer=OfficerProfile(
            id=officer.id,
            name=officer.name,
            role=officer.role.value,
            district=officer.district,
            state=officer.state,
            badge_id=officer.badge_id,
        ),
    )



# ── POST /auth/logout ─────────────────────────────────────────────────────────

@router.post(
    "/logout",
    summary="Officer logout — logs the event",
    description=(
        "Stateless logout: the JWT is not server-side revoked (v1 scope). "
        "The client must discard the token. The event is written to the audit log."
    ),
)
async def logout(
    officer: TokenPayload = Depends(get_current_officer),
    db: AsyncSession = Depends(get_db),
):
    await log_action(
        db,
        actor=officer.sub,
        action="logout",
        case_id=None,
        details={
            "role": officer.role,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    return {"detail": "Logged out successfully"}


# ── GET /auth/me ──────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=OfficerProfile,
    summary="Return the currently logged-in officer's profile",
    description=(
        "Pawan's screens can call this on page-load to rehydrate the officer "
        "profile from the stored JWT without a full login round-trip."
    ),
)
async def me(
    officer: TokenPayload = Depends(get_current_officer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Officers).where(Officers.id == int(officer.sub))
    )
    db_officer = result.scalar_one_or_none()
    if not db_officer:
        raise HTTPException(status_code=404, detail="Officer not found")

    return OfficerProfile(
        id=db_officer.id,
        name=db_officer.name,
        role=db_officer.role.value,
        district=db_officer.district,
        state=db_officer.state,
        badge_id=db_officer.badge_id,
    )
