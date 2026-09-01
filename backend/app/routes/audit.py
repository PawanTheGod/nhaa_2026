from datetime import datetime
from typing import Any, Optional

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLogs


async def log_action(
    db: AsyncSession,
    actor: str,
    action: str,
    case_id: Optional[int] = None,
    details: Optional[dict[str, Any]] = None,
) -> None:
    """
    Append a row to the audit_log table.

    This table is **append-only** — it must never be updated or deleted from.
    We use a raw insert to enforce this at the ORM level.
    """
    await db.execute(
        insert(AuditLogs).values(
            actor=actor,
            action=action,
            case_id=case_id,
            details=details,
            timestamp=datetime.utcnow(),
        )
    )
    await db.commit()
