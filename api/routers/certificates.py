import json
from typing import Annotated, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user
from models.models import Link
from utils import mailer_util

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_auth_dep(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


def _image_subtype(filename: str) -> str:
    ext = (filename or "").rsplit(".", 1)[-1].lower()
    return "png" if ext == "png" else "jpeg"


def _public_links_html(db: Session, event_id: int) -> str:
    """The event's current public Links (same ones on the event page's
    Links tab, e.g. photo gallery / presentations) as a 'Useful links' HTML
    block — fetched fresh from the DB at send time rather than trusted from
    the client, so it always reflects whatever's actually public right now."""
    if not event_id:
        return ""
    rows = (
        db.query(Link)
        .filter(Link.event_id == event_id, Link.deleted_at == None, Link.access_level == "public")
        .order_by(Link.id.asc())
        .all()
    )
    return mailer_util.links_to_html([{"label": l.name, "url": l.link} for l in rows])


DEFAULT_SUBJECT = "Your certificate — ECSACONM Events"


@router.post("/send")
async def send_certificate(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    recipient_email: str = Form(...),
    recipient_name: str = Form(...),
    event_id: int = Form(None),
    subject: str = Form(None),
    message: str = Form(None),
    image: UploadFile = File(...),
    pdf: UploadFile = File(...),
):
    """Email one person their certificate — the message body shows the
    certificate (rendered client-side to both a preview image and a PDF,
    uploaded here) inline, optionally preceded by a short admin-typed
    message and followed by the event's current public Links (photo
    gallery, presentations, etc. — same ones on the event page's Links tab).
    The file the recipient keeps/downloads is the PDF, not the preview image
    (email clients can't render a PDF inline, so the image is still what's
    shown in the body). Mirrors the gala-invitation image email.
    `subject`/`message` are exactly what the admin previewed and edited
    client-side — sent as-is, not re-templated here."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    if not recipient_email or not recipient_email.strip():
        raise HTTPException(status_code=400, detail="recipient_email is required")

    image_bytes = await image.read()
    pdf_bytes = await pdf.read()
    if not image_bytes or not pdf_bytes:
        raise HTTPException(status_code=400, detail="Empty certificate image or PDF")

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
            links_html=_public_links_html(db, event_id),
            attachment_bytes=pdf_bytes,
            attachment_filename=f"Certificate - {recipient_name}.pdf",
            attachment_content_type="application/pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send certificate email: {e}")

    return {"sent": 1, "recipient": recipient_email}


@router.post("/send-bulk")
async def send_certificates_bulk(
    current_user: user_dependency,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    manifest: str = Form(...),
    event_id: int = Form(None),
    images: List[UploadFile] = File(...),
    pdfs: List[UploadFile] = File(...),
):
    """Email a batch of personalised certificates in one go.

    `manifest` is a JSON array of {filename, pdf_filename, email, name,
    subject, message} — one entry per recipient, subject/message already
    personalized client-side (e.g. {{name}} substituted) exactly as
    previewed — matched up against the uploaded `images`/`pdfs` by filename.
    Each recipient gets their own certificate shown inline in the email body
    (same as /send) with their own PDF as the actual attachment, followed by
    the event's current public Links, sent over a single pooled SMTP
    connection via mailer_util.send_bulk_emails
    (backgrounded, same pattern as send_gala_invitations, so a large batch
    doesn't block the request) rather than one connection per recipient.
    Entries with no email (e.g. hand-typed names not tied to a registration)
    should already be filtered out client-side, but are skipped defensively
    here too.
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
    by_pdf_filename = {}
    for f in pdfs:
        by_pdf_filename[f.filename] = await f.read()

    links_html = _public_links_html(db, event_id)
    jobs = []
    skipped = 0
    for entry in entries:
        filename = entry.get("filename")
        pdf_filename = entry.get("pdf_filename")
        email = (entry.get("email") or "").strip()
        name = entry.get("name") or ""
        image_bytes = by_filename.get(filename)
        pdf_bytes = by_pdf_filename.get(pdf_filename)
        if not email or not image_bytes or not pdf_bytes:
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
            "inline_links_html": links_html,
            "inline_attachment_bytes": pdf_bytes,
            "inline_attachment_filename": f"Certificate - {name}.pdf",
            "inline_attachment_content_type": "application/pdf",
        })

    if jobs:
        background_tasks.add_task(mailer_util.send_bulk_emails, jobs)

    return {"queued": len(jobs), "skipped": skipped}
