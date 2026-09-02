"""
app/auth/hashing.py
───────────────────
bcrypt password hashing helpers.  Uses passlib so the algorithm can be
upgraded later without touching call-sites.
"""
from passlib.context import CryptContext

_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the stored *hashed* value."""
    return _ctx.verify(plain, hashed)
