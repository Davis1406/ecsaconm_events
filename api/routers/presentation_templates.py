"""
Presentation Templates – admin-managed downloadable files (PPT, PPTX, DOCX, PDF)
that presenters use when preparing their conference presentations.
"""
import os
import uuid
from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth_dependency import get_current_user
from models.models import PresentationTemplate, User

router = APIRouter()

UPLOAD_DIR = "uploads/presentation_templates"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".ppt", ".pptx", ".doc", ".docx", ".pdf", ".zip"}
MAX_SIZE_MB = 50


def _ext(filename: str) -> str:
    return os.path.splitext(filename)[-1].lower()


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("")
def list_templates(db: Session = Depends(get_db)):
    rows = (
        db.query(PresentationTemplate)
        .filter(PresentationTemplate.deleted_at == None)
        .order_by(PresentationTemplate.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "original_name": r.original_name,
            "description": r.description,
            "file_size": r.file_size,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "uploader": (
                f"{r.uploader.firstname} {r.uploader.lastname}"
                if r.uploader else None
            ),
        }
        for r in rows
    ]


# ── Upload (admin only) ───────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_template(
    file: UploadFile = File(...),
    description: str = Form(""),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = _ext(file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_SIZE_MB} MB limit")

    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(stored_path, "wb") as fh:
        fh.write(content)

    tpl = PresentationTemplate(
        filename=stored_path,
        original_name=file.filename or stored_name,
        description=description or None,
        file_size=len(content),
        uploaded_by=current_user["user_id"],
    )
    db.add(tpl)
    db.commit()
    db.refresh(tpl)

    return {"id": tpl.id, "original_name": tpl.original_name, "file_size": tpl.file_size}


# ── Download ──────────────────────────────────────────────────────────────────

@router.get("/{template_id}/download")
def download_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    tpl = (
        db.query(PresentationTemplate)
        .filter(
            PresentationTemplate.id == template_id,
            PresentationTemplate.deleted_at == None,
        )
        .first()
    )
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    if not os.path.exists(tpl.filename):
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(
        path=tpl.filename,
        filename=tpl.original_name,
        media_type="application/octet-stream",
    )


# ── Delete (soft, admin only) ─────────────────────────────────────────────────

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tpl = (
        db.query(PresentationTemplate)
        .filter(
            PresentationTemplate.id == template_id,
            PresentationTemplate.deleted_at == None,
        )
        .first()
    )
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")

    tpl.deleted_at = datetime.now(timezone.utc)
    db.commit()
