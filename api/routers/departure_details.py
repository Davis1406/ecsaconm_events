import secrets
from typing import Annotated, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user
from models.models import (
    DepartureDetail,
    Event,
    ParticipationRole,
    Registration,
    SystemSetting,
    User,
)

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]

DIGEST_BATCH_SIZE = 20
VIEW_TOKEN_SETTING_KEY = "departure_details_view_token"


def get_auth_dep(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


def _get_or_create_view_token(db: Session) -> str:
    """A single standing secret that lets lemmym@/info@ open the live
    submissions list by URL alone, no login — generated once and reused
    (not per-person, since this link is shared by two people)."""
    row = db.query(SystemSetting).filter_by(key=VIEW_TOKEN_SETTING_KEY).first()
    if row and row.value:
        return row.value
    token = secrets.token_urlsafe(32)
    if row:
        row.value = token
    else:
        row = SystemSetting(key=VIEW_TOKEN_SETTING_KEY, value=token)
        db.add(row)
    db.commit()
    return token


def _eligible_registrants(db: Session, event_id: Optional[int] = None):
    """Paid, non-secretariat registrants — the audience for the travel
    details form. Secretariat is excluded outright regardless of its
    always-true is_paid status; everyone else must actually be paid."""
    q = (
        db.query(Registration)
        .join(Registration.user)
        .options(joinedload(Registration.user))
        .filter(
            Registration.deleted_at == None,
            Registration.paid == True,
            Registration.participation_role != ParticipationRole.secretariat,
        )
    )
    if event_id:
        q = q.filter(Registration.event_id == event_id)

    results = []
    seen_emails = set()
    for r in q.all():
        user = r.user
        if not user or not user.email:
            continue
        email = user.email.strip().lower()
        if email in seen_emails:
            continue
        seen_emails.add(email)
        results.append({
            "email": email,
            "name": f"{user.firstname or ''} {user.lastname or ''}".strip() or email,
            "registration_id": r.id,
            "event_id": r.event_id,
        })
    return results


def _serialize(rec: DepartureDetail):
    return {
        "id": rec.id,
        "event_id": rec.event_id,
        "email": rec.email,
        "name": rec.name,
        "hotel": rec.hotel,
        "departure_date": rec.departure_date,
        "departure_time": rec.departure_time,
        "submitted": rec.submitted_at is not None,
        "submitted_at": rec.submitted_at.isoformat() if rec.submitted_at else None,
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
    }


@router.get("/recipients")
def list_recipients(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(None),
):
    """Admin view: eligible (paid, non-secretariat) registrants with their
    form/submission status."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    people = _eligible_registrants(db, event_id)
    out = []
    for p in people:
        rec = (
            db.query(DepartureDetail)
            .filter(
                DepartureDetail.email == p["email"],
                DepartureDetail.event_id == p["event_id"],
                DepartureDetail.deleted_at == None,
            )
            .first()
        )
        out.append({
            **p,
            "has_form": rec is not None,
            "token": rec.token if rec else None,
            "submitted": bool(rec and rec.submitted_at),
        })
    return out


class SendFormBody(BaseModel):
    event_id: Optional[int] = None
    selected_emails: Optional[list] = None
    test_email: Optional[str] = None


@router.post("/send")
def send_departure_forms(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    body: SendFormBody = None,
):
    """Generate a personal form link for each selected (or all) eligible
    registrant and email it to them. Pass `test_email` to fire a single
    trial send immediately (using a sample link, nothing persisted/queued)."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])

    body = body or SendFormBody()
    import utils.mailer_util as mailer_util

    event = db.query(Event).filter(Event.id == body.event_id).first() if body.event_id else db.query(Event).first()
    event_name = event.event if event else "ECSACONM Scientific Conference"

    if body.test_email:
        subject, html = _build_invitation_email(event_name, "Sample Participant", f"{mailer_util.CLIENT_ORIGIN}/#/travel-details/sample-token")
        mailer_util.send_email(body.test_email, subject, html, email_type="departure_details_invitation", sent_by_user_id=current_user["user_id"])
        return {"sent": 1, "message": f"Sample invitation sent to {body.test_email}."}

    event_id = body.event_id
    selected_set = (
        {e.strip().lower() for e in body.selected_emails} if body.selected_emails else None
    )

    people = _eligible_registrants(db, event_id)
    recipients = []
    for p in people:
        if selected_set is not None and p["email"] not in selected_set:
            continue
        rec = (
            db.query(DepartureDetail)
            .filter(
                DepartureDetail.email == p["email"],
                DepartureDetail.event_id == p["event_id"],
                DepartureDetail.deleted_at == None,
            )
            .first()
        )
        if not rec:
            rec = DepartureDetail(
                event_id=p["event_id"],
                registration_id=p["registration_id"],
                email=p["email"],
                name=p["name"],
                token=secrets.token_urlsafe(24),
            )
            db.add(rec)
            db.commit()
            db.refresh(rec)
        recipients.append({**p, "token": rec.token})

    jobs = []
    for r in recipients:
        form_link = f"{mailer_util.CLIENT_ORIGIN}/#/travel-details/{r['token']}"
        subject, html = _build_invitation_email(event_name, r["name"], form_link)
        jobs.append({
            "recipient_email": r["email"],
            "subject": subject,
            "email_body": html,
            "email_type": "departure_details_invitation",
            "sent_by_user_id": current_user["user_id"],
        })

    sent = len(jobs)
    if jobs:
        background_tasks.add_task(mailer_util.send_bulk_emails, jobs)

    return {
        "sent": sent,
        "message": f"Travel-details form queued for {sent} paid, non-secretariat registrant(s).",
    }


def _build_invitation_email(event_name, name, form_link):
    subject = f"Please Share Your Travel & Hotel Details — {event_name}"
    html = (
        f"<p>Dear {name},</p>"
        f"<p>As we finalise logistics for <strong>{event_name}</strong>, kindly let us know "
        f"your hotel and departure details using the short form below.</p>"
        f"<p><a href=\"{form_link}\" style=\"display:inline-block;padding:12px 28px;"
        f"background-color:rgb(254,80,103);color:#ffffff;text-decoration:none;"
        f"border-radius:8px;font-weight:600;\">Submit Travel Details</a></p>"
        f"<p>If the button doesn't work, copy and paste this link into your browser:<br>"
        f"<span style=\"color:#6b7280;\">{form_link}</span></p>"
        f"<p>Thank you,<br>ECSACONM Secretariat</p>"
    )
    return subject, html


def _build_receipt_email(event_name, name, hotel, departure_date, departure_time):
    subject = f"Received — Your Travel Details for {event_name}"
    html = (
        f"<p>Dear {name},</p>"
        f"<p>Thank you — we've received your travel details:</p>"
        f"<table style=\"border-collapse:collapse;font-size:14px;\">"
        f"<tr><td style=\"padding:4px 12px 4px 0;color:#6b7280;\">Hotel</td><td><strong>{hotel or '—'}</strong></td></tr>"
        f"<tr><td style=\"padding:4px 12px 4px 0;color:#6b7280;\">Departure date</td><td><strong>{departure_date or '—'}</strong></td></tr>"
        f"<tr><td style=\"padding:4px 12px 4px 0;color:#6b7280;\">Departure time</td><td><strong>{departure_time or '—'}</strong></td></tr>"
        f"</table>"
        f"<p>If any of this changes, just submit the form again using the same link.</p>"
        f"<p>Thank you,<br>ECSACONM Secretariat</p>"
    )
    return subject, html


def _build_digest_email(event_name, entries, total):
    subject = f"Travel Details — {len(entries)} New Submissions ({event_name})"
    rows = "".join(
        f"<tr><td style='padding:4px 10px;border-bottom:1px solid #eee;'>{e.name or e.email}</td>"
        f"<td style='padding:4px 10px;border-bottom:1px solid #eee;'>{e.hotel or '—'}</td>"
        f"<td style='padding:4px 10px;border-bottom:1px solid #eee;'>{e.departure_date or '—'}</td>"
        f"<td style='padding:4px 10px;border-bottom:1px solid #eee;'>{e.departure_time or '—'}</td></tr>"
        for e in entries
    )
    html = (
        f"<p>{len(entries)} more registrants have submitted their travel details for "
        f"<strong>{event_name}</strong> ({total} total submitted so far).</p>"
        f"<table style=\"border-collapse:collapse;font-size:13px;width:100%;\">"
        f"<tr style=\"text-align:left;color:#6b7280;\"><th style='padding:4px 10px;'>Name</th>"
        f"<th style='padding:4px 10px;'>Hotel</th><th style='padding:4px 10px;'>Departure date</th>"
        f"<th style='padding:4px 10px;'>Departure time</th></tr>{rows}</table>"
        f"<p style=\"margin-top:16px;\">View the full, live list any time — no login needed:<br>"
        f"<a href=\"{{VIEW_LINK}}\">{{VIEW_LINK}}</a></p>"
    )
    return subject, html


@router.get("/form/{token}")
def get_departure_form(token: str, db: Session = Depends(get_db)):
    """Public, no-auth: fetch the form details for a registrant's personal link."""
    rec = (
        db.query(DepartureDetail)
        .options(joinedload(DepartureDetail.event))
        .filter(DepartureDetail.token == token, DepartureDetail.deleted_at == None)
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Form link is invalid or has expired.")
    return {
        "name": rec.name,
        "email": rec.email,
        "event_name": rec.event.event if rec.event else "ECSACONM Event",
        "already_submitted": rec.submitted_at is not None,
        "hotel": rec.hotel,
        "departure_date": rec.departure_date,
        "departure_time": rec.departure_time,
    }


class SubmitFormBody(BaseModel):
    hotel: str
    departure_date: str
    departure_time: str


@router.post("/form/{token}")
def submit_departure_form(
    token: str,
    body: SubmitFormBody,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Public, no-auth: record the registrant's travel details, email them a
    receipt, and — every DIGEST_BATCH_SIZE submissions — send lemmym@/info@
    a batch digest instead of pinging them on every single one."""
    rec = (
        db.query(DepartureDetail)
        .options(joinedload(DepartureDetail.event))
        .filter(DepartureDetail.token == token, DepartureDetail.deleted_at == None)
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Form link is invalid or has expired.")

    from datetime import datetime, timezone
    rec.hotel = (body.hotel or "").strip()
    rec.departure_date = (body.departure_date or "").strip()
    rec.departure_time = (body.departure_time or "").strip()
    rec.submitted_at = datetime.now(timezone.utc)
    db.commit()

    import utils.mailer_util as mailer_util
    event_name = rec.event.event if rec.event else "ECSACONM Event"

    subject, html = _build_receipt_email(event_name, rec.name or rec.email, rec.hotel, rec.departure_date, rec.departure_time)
    background_tasks.add_task(
        mailer_util.send_email, rec.email, subject, html,
        "departure_details_receipt", None,
    )

    total_submitted = (
        db.query(DepartureDetail)
        .filter(
            DepartureDetail.event_id == rec.event_id,
            DepartureDetail.deleted_at == None,
            DepartureDetail.submitted_at != None,
        )
        .count()
    )
    if total_submitted % DIGEST_BATCH_SIZE == 0:
        batch = (
            db.query(DepartureDetail)
            .filter(
                DepartureDetail.event_id == rec.event_id,
                DepartureDetail.deleted_at == None,
                DepartureDetail.submitted_at != None,
            )
            .order_by(DepartureDetail.submitted_at.desc())
            .limit(DIGEST_BATCH_SIZE)
            .all()
        )
        token_v = _get_or_create_view_token(db)
        view_link = f"{mailer_util.CLIENT_ORIGIN}/#/travel-details-report/{token_v}?event_id={rec.event_id}"
        subject, html = _build_digest_email(event_name, list(reversed(batch)), total_submitted)
        html = html.replace("{VIEW_LINK}", view_link)
        for to in ("lemmym@ecsaconm.org", "info@ecsaconm.org"):
            background_tasks.add_task(
                mailer_util.send_email, to, subject, html,
                "departure_details_digest", None,
            )

    return {
        "message": "Thank you! Your travel details have been recorded.",
        "hotel": rec.hotel,
        "departure_date": rec.departure_date,
        "departure_time": rec.departure_time,
    }


@router.get("/public-view/{token}")
def public_view(
    token: str,
    db: Session = Depends(get_db),
    event_id: int = Query(None),
):
    """Public, no-auth: the live submissions list, reachable only by whoever
    has this unguessable link (sent to lemmym@/info@) — same trust model as
    the app's other public-by-link views (room-view, document QR, etc.)."""
    real_token = _get_or_create_view_token(db)
    if token != real_token:
        raise HTTPException(status_code=404, detail="Not found.")

    q = db.query(DepartureDetail).filter(DepartureDetail.deleted_at == None)
    if event_id:
        q = q.filter(DepartureDetail.event_id == event_id)
    records = q.order_by(DepartureDetail.submitted_at.desc().nullslast(), DepartureDetail.created_at.desc()).all()

    event = db.query(Event).filter(Event.id == event_id).first() if event_id else None
    return {
        "event_name": event.event if event else None,
        "total_recipients": len(records),
        "total_submitted": sum(1 for r in records if r.submitted_at),
        "data": [_serialize(r) for r in records],
    }


@router.get("/view-link")
def get_view_link(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(None),
):
    """Admin: the standing no-login URL to hand to lemmym@/info@."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    import utils.mailer_util as mailer_util
    token = _get_or_create_view_token(db)
    link = f"{mailer_util.CLIENT_ORIGIN}/#/travel-details-report/{token}"
    if event_id:
        link += f"?event_id={event_id}"
    return {"link": link}


@router.post("/sample-receipt")
def send_sample_receipt(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    to_email: str = Query(...),
    event_id: int = Query(None),
):
    """Admin: fire a one-off sample of the post-submission receipt email
    using placeholder data, so the wording/format can be reviewed."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    import utils.mailer_util as mailer_util
    event = db.query(Event).filter(Event.id == event_id).first() if event_id else db.query(Event).first()
    event_name = event.event if event else "ECSACONM Scientific Conference"
    subject, html = _build_receipt_email(event_name, "Jane Sample Delegate", "Sample Grand Hotel", "2026-09-20", "10:30")
    mailer_util.send_email(to_email, subject, html, email_type="departure_details_receipt", sent_by_user_id=current_user["user_id"])
    return {"sent": 1, "message": f"Sample receipt sent to {to_email}."}
