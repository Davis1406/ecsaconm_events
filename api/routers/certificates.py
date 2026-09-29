import json
from typing import Annotated, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user
from sqlalchemy import func

from models.models import EmailLog, Link, User
from utils import mailer_util
from utils.page_ref import with_ref

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_auth_dep(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


def _image_subtype(filename: str) -> str:
    ext = (filename or "").rsplit(".", 1)[-1].lower()
    return "png" if ext == "png" else "jpeg"


def _public_links(db: Session, event_id: int) -> list:
    """The event's current public Links (same ones on the event page's
    Links tab, e.g. photo gallery / presentations) — fetched fresh from the
    DB at send time rather than trusted from the client, so it always
    reflects whatever's actually public right now."""
    if not event_id:
        return []
    return (
        db.query(Link)
        .filter(Link.event_id == event_id, Link.deleted_at == None, Link.access_level == "public")
        .order_by(Link.id.asc())
        .all()
    )


def _links_html(links: list, user_id=None) -> str:
    """'Useful links' block for one recipient. The public programme link gets
    their signed ref (utils/page_ref.py) so page-view stats can show who
    opened it from their email; other links are unchanged."""
    return mailer_util.links_to_html([{"label": l.name, "url": with_ref(l.link, user_id)} for l in links])


def _user_ids_by_email(db: Session, emails) -> dict:
    wanted = {(e or "").strip().lower() for e in emails if e and e.strip()}
    if not wanted:
        return {}
    rows = (
        db.query(User.id, User.email)
        .filter(User.deleted_at == None, func.lower(User.email).in_(wanted))
        .all()
    )
    return {email.strip().lower(): uid for uid, email in rows}


DEFAULT_SUBJECT = "Your certificate — ECSACONM Events"


@router.get("/sent")
async def sent_certificates(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    """The set of recipient emails that have already received a successfully
    sent certificate (email_type=certificate, status=sent). The Certificates
    page uses this to show a "Sent" label next to people who already got
    theirs, and to offer Resend (which reopens the same preview/edit modal)."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    rows = (
        db.query(EmailLog.recipient_email)
        .filter(
            EmailLog.email_type == "certificate",
            EmailLog.status == "sent",
        )
        .all()
    )
    emails = sorted({r[0].strip().lower() for r in rows if r[0] and r[0].strip()})
    return {"sent": emails, "total": len(emails)}


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
            links_html=_links_html(
                _public_links(db, event_id),
                _user_ids_by_email(db, [recipient_email]).get(recipient_email.strip().lower()),
            ),
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

    links = _public_links(db, event_id)
    user_ids = _user_ids_by_email(db, [e.get("email") for e in entries])
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
            "inline_links_html": _links_html(links, user_ids.get(email.lower())),
            "inline_attachment_bytes": pdf_bytes,
            "inline_attachment_filename": f"Certificate - {name}.pdf",
            "inline_attachment_content_type": "application/pdf",
        })

    if jobs:
        background_tasks.add_task(mailer_util.send_bulk_emails, jobs)

    return {"queued": len(jobs), "skipped": skipped}
