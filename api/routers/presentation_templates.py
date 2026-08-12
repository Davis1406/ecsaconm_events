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
from models.models import PresentationTemplate, PresentationType, User

router = APIRouter()

UPLOAD_DIR = "uploads/presentation_templates"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".ppt", ".pptx", ".doc", ".docx", ".pdf", ".zip"}
MAX_SIZE_MB = 50

PREVIEW_MEDIA_TYPES = {
    ".pdf": "application/pdf",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _ext(filename: str) -> str:
    return os.path.splitext(filename)[-1].lower()


def _get_template_or_404(template_id: int, db: Session) -> PresentationTemplate:
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
    return tpl


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
            "presentation_type": r.presentation_type.value if r.presentation_type else "either",
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
    presentation_type: str = Form("either"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = _ext(file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    try:
        ptype = PresentationType(presentation_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"presentation_type must be one of: {', '.join(t.value for t in PresentationType)}",
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
        presentation_type=ptype,
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
    tpl = _get_template_or_404(template_id, db)
    return FileResponse(
        path=tpl.filename,
        filename=tpl.original_name,
        media_type="application/octet-stream",
    )


# ── Preview ───────────────────────────────────────────────────────────────────
# Served without Content-Disposition: attachment so it can be rendered inline
# (PDF directly in an <iframe>; Office formats via an external embed viewer
# that fetches this URL — it must stay unauthenticated/public for that to work).

@router.get("/{template_id}/preview")
def preview_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    tpl = _get_template_or_404(template_id, db)
    ext = _ext(tpl.original_name)
    media_type = PREVIEW_MEDIA_TYPES.get(ext)
    if not media_type:
        raise HTTPException(status_code=415, detail="Preview not supported for this file type")

    return FileResponse(path=tpl.filename, media_type=media_type)


# ── Update metadata (admin only) ────────────────────────────────────────────────
# Re-tag an existing template's audience (oral/poster/either) or description
# without having to delete and re-upload the file.

@router.patch("/{template_id}")
def update_template(
    template_id: int,
    presentation_type: str = Form(None),
    description: str = Form(None),
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

    if presentation_type is not None:
        try:
            tpl.presentation_type = PresentationType(presentation_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"presentation_type must be one of: {', '.join(t.value for t in PresentationType)}",
            )
    if description is not None:
        tpl.description = description or None

    db.commit()
    db.refresh(tpl)
    return {
        "id": tpl.id,
        "original_name": tpl.original_name,
        "description": tpl.description,
        "presentation_type": tpl.presentation_type.value,
    }


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
