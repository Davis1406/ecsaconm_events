from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user
from models.models import EmailLog

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]

# 1x1 transparent GIF
_PIXEL_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
    b"\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
    b"\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
)


def get_auth_dep(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


# ── Public tracking pixel — no auth so email clients can fetch it ─────────────
@router.get("/{log_id}/pixel.png", include_in_schema=False)
def track_email_open(log_id: int, db: Session = Depends(get_db)):
    log = db.query(EmailLog).filter(EmailLog.id == log_id).first()
    if log:
        if not log.opened_at:
            log.opened_at = datetime.utcnow()
        log.opened_count = (log.opened_count or 0) + 1
        db.commit()
    return Response(
        content=_PIXEL_GIF,
        media_type="image/gif",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
    )


# ── List ──────────────────────────────────────────────────────────────────────
@router.get("/")
def list_email_logs(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    skip: int = 0,
    limit: int = 500,
    email_type: str = None,
):
    auth_dependency.secure_access("VIEW_USER", current_user["user_id"])
    q = db.query(EmailLog).options(joinedload(EmailLog.sent_by))
    if email_type:
        q = q.filter(EmailLog.email_type == email_type)
    total = q.count()
    logs = q.order_by(EmailLog.sent_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "data": [_serialize(log) for log in logs],
    }


# ── Stats (report) ──────────────────────────────────────────────────────────
@router.get("/stats/summary")
def get_email_log_stats(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    """Aggregate counts for the Sent Emails report: by type, by status, and
    opened vs not-opened among successfully sent emails."""
    auth_dependency.secure_access("VIEW_USER", current_user["user_id"])

    by_type = (
        db.query(EmailLog.email_type, func.count(EmailLog.id))
        .group_by(EmailLog.email_type)
        .all()
    )
    by_status = (
        db.query(EmailLog.status, func.count(EmailLog.id))
        .group_by(EmailLog.status)
        .all()
    )
    sent_total = db.query(func.count(EmailLog.id)).filter(EmailLog.status == "sent").scalar() or 0
    opened = db.query(func.count(EmailLog.id)).filter(
        EmailLog.status == "sent", EmailLog.opened_count > 0
    ).scalar() or 0

    return {
        "by_type": [{"email_type": t or "general", "count": c} for t, c in by_type],
        "by_status": [{"status": s, "count": c} for s, c in by_status],
        "opened": {
            "opened": opened,
            "not_opened": sent_total - opened,
            "sent_total": sent_total,
        },
    }


# ── Bulk delete: failed only ────────────────────────────────────────────────
@router.delete("/failed/all")
def clear_failed_email_logs(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("VIEW_USER", current_user["user_id"])
    deleted = db.query(EmailLog).filter(EmailLog.status == "failed").delete(synchronize_session=False)
    db.commit()
    return {"detail": f"Deleted {deleted} failed log(s).", "deleted": deleted}


# ── Bulk resend: failed only ────────────────────────────────────────────────
@router.post("/failed/resend")
def resend_failed_email_logs(
    current_user: user_dependency,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    body: dict = None,
):
    """Retry sending every currently-failed email log (or a selected subset
    via `log_ids` in the body), reusing its originally stored subject/body."""
    auth_dependency.secure_access("VIEW_USER", current_user["user_id"])

    log_ids = (body or {}).get("log_ids")
    q = db.query(EmailLog).filter(EmailLog.status == "failed")
    if log_ids:
        q = q.filter(EmailLog.id.in_(log_ids))
    failed_logs = q.all()

    jobs = [
        {
            "recipient_email": log.recipient_email,
            "subject": log.subject,
            "email_body": log.body,
            "email_type": log.email_type,
            "sent_by_user_id": current_user["user_id"],
            "reply_to_email": log.reply_to_email,
        }
        for log in failed_logs
        if log.body  # older rows from before body storage was added have nothing to resend
    ]
    skipped = len(failed_logs) - len(jobs)

    import utils.mailer_util as mailer_util
    if jobs:
        background_tasks.add_task(mailer_util.send_bulk_emails, jobs)

    return {
        "queued": len(jobs),
        "skipped_no_body": skipped,
        "message": f"Resending {len(jobs)} failed email(s)."
                    + (f" {skipped} skipped (no stored content)." if skipped else ""),
    }


# ── Delete ───────────────────────────────────────────────────────────────────
@router.delete("/{log_id}")
def delete_email_log(
    log_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("VIEW_USER", current_user["user_id"])
    log = db.query(EmailLog).filter(EmailLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Email log not found")
    db.delete(log)
    db.commit()
    return {"detail": "Deleted"}


# ── Detail ────────────────────────────────────────────────────────────────────
@router.get("/{log_id}")
def get_email_log(
    log_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("VIEW_USER", current_user["user_id"])
    log = (
        db.query(EmailLog)
        .options(joinedload(EmailLog.sent_by))
        .filter(EmailLog.id == log_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Email log not found")
    return {**_serialize(log), "body": log.body}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _serialize(log: EmailLog) -> dict:
    return {
        "id": log.id,
        "recipient_email": log.recipient_email,
        "subject": log.subject,
        "email_type": log.email_type,
        "sent_by": f"{log.sent_by.firstname} {log.sent_by.lastname}" if log.sent_by else None,
        "sent_by_email": log.sent_by.email if log.sent_by else None,
        "reply_to_email": log.reply_to_email,
        "status": log.status,
        "error_message": log.error_message,
        "sent_at": log.sent_at,
        "opened_at": log.opened_at,
        "opened_count": log.opened_count or 0,
    }
