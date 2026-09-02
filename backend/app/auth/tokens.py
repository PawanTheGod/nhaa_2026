"""
app/auth/tokens.py
──────────────────
JWT creation and decoding.

Claims stored in every token:
  sub          – officer id (str)
  role         – OfficerRole value  (e.g. "operator", "police", "ministry")
  district     – nullable str
  state        – nullable str
  exp          – standard expiry

All free/open-source: python-jose with HS256.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings


# ── Token payload schema (returned by decode_access_token) ────────────────────

class TokenPayload(BaseModel):
    sub: str                   # officer id as string
    role: str                  # OfficerRole value
    name: Optional[str] = None # Officer full name
    district: Optional[str] = None
    state: Optional[str] = None
    exp: datetime


# ── Create ────────────────────────────────────────────────────────────────────

def create_access_token(
    officer_id: int,
    role: str,
    name: Optional[str] = None,
    district: Optional[str] = None,
    state: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Sign and return a JWT containing the officer's identity, name, and scope claims.

    :param officer_id: PK from the officers table
    :param role:       OfficerRole enum value (string)
    :param name:       Officer name
    :param district:   Officer's district (None for state/ministry)
    :param state:      Officer's state (None for ministry)
    :param expires_delta: Override default expiry (useful in tests)
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": str(officer_id),
        "role": role,
        "name": name,
        "district": district,
        "state": state,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


# ── Decode ────────────────────────────────────────────────────────────────────

def decode_access_token(token: str) -> TokenPayload:
    """
    Verify signature and expiry, then return a typed TokenPayload.

    Raises:
        jose.JWTError – if the token is invalid or expired
        (callers convert this to HTTP 401)
    """
    raw = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    return TokenPayload(
        sub=raw["sub"],
        role=raw["role"],
        name=raw.get("name"),
        district=raw.get("district"),
        state=raw.get("state"),
        exp=datetime.fromtimestamp(raw["exp"], tz=timezone.utc),
    )
