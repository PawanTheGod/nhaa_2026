"""
app/routes/evidence.py
───────────────────────
Evidence file management for cases: upload, list, download, and delete.
Files are stored locally in uploads/evidence/{case_id}/ and tracked in the database.
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_officer
from app.auth.tokens import TokenPayload
from app.database import get_db
from app.models import AuditLogs, CaseEvidence, Cases, Officers
from app.schemas import EvidenceOut

router = APIRouter(tags=["Evidence Management"])

UPLOAD_DIR = Path("uploads/evidence")


@router.post("/cases/{case_id}/evidence", response_model=list[EvidenceOut], status_code=status.HTTP_201_CREATED)
async def upload_case_evidence(
    case_id: int,
    files: list[UploadFile] = File(...),
    description: Optional[str] = Form(None),
    tier_level: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    """Upload one or more evidence files for a case."""
    res = await db.execute(select(Cases).where(Cases.id == case_id))
    case = res.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case #{case_id} not found")

    target_dir = UPLOAD_DIR / str(case_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    # Resolve uploader officer id if exists
    off_res = await db.execute(select(Officers).where(Officers.username == officer.sub))
    db_officer = off_res.scalar_one_or_none()
    uploader_id = db_officer.id if db_officer else None
    tier = tier_level or officer.role

    results = []
    for upload in files:
        # Sanitize filename
        safe_name = Path(upload.filename).name.replace(" ", "_")
        dest_path = target_dir / safe_name

        # If file already exists, avoid collision
        counter = 1
        base_stem = Path(safe_name).stem
        base_suffix = Path(safe_name).suffix
        while dest_path.exists():
            safe_name = f"{base_stem}_{counter}{base_suffix}"
            dest_path = target_dir / safe_name
            counter += 1

        # Write file content
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)

        file_size = dest_path.stat().st_size
        relative_path = f"uploads/evidence/{case_id}/{safe_name}"

        evidence_record = CaseEvidence(
            case_id=case_id,
            uploaded_by=uploader_id,
            file_name=safe_name,
            file_path=relative_path,
            file_type=upload.content_type,
            file_size=file_size,
            description=description,
            tier_level=tier,
        )
        db.add(evidence_record)
        results.append(evidence_record)

    await db.flush()

    # Log audit entry
    db.add(
        AuditLogs(
            actor=f"{officer.role}:{officer.sub}",
            action="evidence_uploaded",
            case_id=case_id,
            details={"files_count": len(files), "tier": tier},
        )
    )
    await db.commit()

    for item in results:
        await db.refresh(item)

    return results


@router.get("/cases/{case_id}/evidence", response_model=list[EvidenceOut])
async def list_case_evidence(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    """Retrieve all evidence files associated with a case."""
    res = await db.execute(
        select(CaseEvidence)
        .where(CaseEvidence.case_id == case_id)
        .order_by(CaseEvidence.uploaded_at.desc())
    )
    return res.scalars().all()


@router.get("/evidence/{evidence_id}/download")
async def download_evidence_file(
    evidence_id: int,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    """Download an evidence file by ID."""
    res = await db.execute(select(CaseEvidence).where(CaseEvidence.id == evidence_id))
    evidence = res.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence record not found")

    file_path = Path(evidence.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Evidence file not found on disk")

    return FileResponse(
        path=str(file_path),
        filename=evidence.file_name,
        media_type=evidence.file_type or "application/octet-stream",
    )


@router.delete("/evidence/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence_file(
    evidence_id: int,
    db: AsyncSession = Depends(get_db),
    officer: TokenPayload = Depends(get_current_officer),
):
    """Delete an evidence record and its file."""
    res = await db.execute(select(CaseEvidence).where(CaseEvidence.id == evidence_id))
    evidence = res.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence record not found")

    file_path = Path(evidence.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            pass

    case_id = evidence.case_id
    await db.delete(evidence)
    db.add(
        AuditLogs(
            actor=f"{officer.role}:{officer.sub}",
            action="evidence_deleted",
            case_id=case_id,
            details={"evidence_id": evidence_id, "file_name": evidence.file_name},
        )
    )
    await db.commit()
    return None
