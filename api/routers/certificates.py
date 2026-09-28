import json
from typing import Annotated, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user
from utils import mailer_util

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_auth_dep(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


def _image_subtype(filename: str) -> str:
    ext = (filename or "").rsplit(".", 1)[-1].lower()
    return "png" if ext == "png" else "jpeg"


DEFAULT_SUBJECT = "Your certificate — ECSACONM Events"


@router.post("/send")
async def send_certificate(
    current_user: user_dependency,
    auth_dependency: Auth = Depends(get_auth_dep),
    recipient_email: str = Form(...),
    recipient_name: str = Form(...),
    subject: str = Form(None),
    message: str = Form(None),
    image: UploadFile = File(...),
):
    """Email one person their certificate — the message body is the
    certificate image (rendered client-side, uploaded here), embedded inline
    and attached again as a file, optionally preceded by a short admin-typed
    message. Mirrors the gala-invitation image email. `subject`/`message`
    are exactly what the admin previewed and edited client-side — sent
    as-is, not re-templated here."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    if not recipient_email or not recipient_email.strip():
        raise HTTPException(status_code=400, detail="recipient_email is required")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty certificate image")

    try:
        mailer_util.send_image_invitation_email(
            recipient_email=recipient_email.strip(),
            subject=subject or f"Your certificate — {recipient_name}",
            image_bytes=image_bytes,
            image_filename=f"Certificate - {recipient_name}.{(image.filename or 'certificate.jpg').rsplit('.', 1)[-1]}",
            image_subtype=_image_subtype(image.filename),
            email_type="certificate",
            sent_by_user_id=current_user["user_id"],
            message_html=mailer_util.text_to_html(message),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send certificate email: {e}")

    return {"sent": 1, "recipient": recipient_email}


@router.post("/send-bulk")
async def send_certificates_bulk(
    current_user: user_dependency,
    background_tasks: BackgroundTasks,
    auth_dependency: Auth = Depends(get_auth_dep),
    manifest: str = Form(...),
    images: List[UploadFile] = File(...),
):
    """Email a batch of personalised certificates in one go.

    `manifest` is a JSON array of {filename, email, name, subject, message}
    — one entry per recipient, subject/message already personalized
    client-side (e.g. {{name}} substituted) exactly as previewed — matched
    up against the uploaded `images` by filename. Each recipient gets their
    own certificate image embedded inline in the email body (same as
    /send), sent over a single pooled SMTP connection via
    mailer_util.send_bulk_emails (backgrounded, same pattern as
    send_gala_invitations, so a large batch doesn't block the request) rather
    than one connection per recipient. Entries with no email (e.g. hand-typed
    names not tied to a registration) should already be filtered out
    client-side, but are skipped defensively here too.
    """
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    try:
        entries = json.loads(manifest)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid manifest JSON")
    if not isinstance(entries, list) or not entries:
        raise HTTPException(status_code=400, detail="manifest must be a non-empty list")

    by_filename = {}
    for img in images:
        by_filename[img.filename] = await img.read()

    jobs = []
    skipped = 0
    for entry in entries:
        filename = entry.get("filename")
        email = (entry.get("email") or "").strip()
        name = entry.get("name") or ""
        image_bytes = by_filename.get(filename)
        if not email or not image_bytes:
            skipped += 1
            continue
        jobs.append({
            "recipient_email": email,
            "subject": entry.get("subject") or f"Your certificate — {name}",
            "email_body": "",
            "email_type": "certificate",
            "sent_by_user_id": current_user["user_id"],
            "inline_image_bytes": image_bytes,
            "inline_image_filename": f"Certificate - {name}.{(filename or 'certificate.jpg').rsplit('.', 1)[-1]}",
            "inline_image_subtype": _image_subtype(filename),
            "inline_message_html": mailer_util.text_to_html(entry.get("message")),
        })

    if jobs:
        background_tasks.add_task(mailer_util.send_bulk_emails, jobs)

    return {"queued": len(jobs), "skipped": skipped}
