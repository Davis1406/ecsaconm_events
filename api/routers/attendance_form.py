import secrets
from typing import Annotated, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user
from models.models import (
    Abstract,
    AbstractAuthor,
    AttendanceFormResponse,
    EmailLog,
    Event,
    Registration,
    User,
)

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_auth_dep(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


def _unregistered_presenters(db: Session, event_id: Optional[int] = None):
    """Accepted-abstract presenters (unique by email) who have not registered
    for the given event — the audience this form targets."""
    q = (
        db.query(AbstractAuthor)
        .join(Abstract, AbstractAuthor.abstract_id == Abstract.id)
        .options(joinedload(AbstractAuthor.abstract).joinedload(Abstract.event))
        .filter(
            AbstractAuthor.is_presenting == True,
            AbstractAuthor.email != None,
            AbstractAuthor.email != "",
            Abstract.status == "accepted",
            Abstract.deleted_at == None,
        )
    )
    if event_id:
        q = q.filter(Abstract.event_id == event_id)

    results = []
    seen_emails = set()
    for pa in q.all():
        email = pa.email.strip().lower()
        if email in seen_emails:
            continue
        seen_emails.add(email)

        user = db.query(User).filter(User.email == email).first()
        has_account = user is not None
        target_event_id = event_id or pa.abstract.event_id

        has_registration = False
        if has_account:
            has_registration = (
                db.query(Registration)
                .filter(
                    Registration.user_id == user.id,
                    Registration.event_id == target_event_id,
                )
                .first()
                is not None
            )
        if has_registration:
            continue

        results.append(
            {
                "firstname": pa.firstname,
                "lastname": pa.lastname,
                "email": email,
                "abstract_title": pa.abstract.title,
                "has_account": has_account,
                "event_id": target_event_id,
                "event_name": pa.abstract.event.event
                if pa.abstract and pa.abstract.event
                else "ECSACONM Event",
            }
        )
    return results


def _serialize_recipient(db: Session, presenter: dict):
    """Merge a presenter with their existing form record + email-log status."""
    rec = (
        db.query(AttendanceFormResponse)
        .filter(
            AttendanceFormResponse.email == presenter["email"],
            AttendanceFormResponse.event_id == presenter["event_id"],
            AttendanceFormResponse.deleted_at == None,
        )
        .first()
    )
    sent = (
        db.query(EmailLog)
        .filter(
            EmailLog.email_type == "attendance_form",
            EmailLog.recipient_email == presenter["email"],
        )
        .first()
        is not None
    )
    return {
        **presenter,
        "has_form": rec is not None,
        "token": rec.token if rec else None,
        "response": rec.response if rec else None,
        "responded_at": rec.responded_at.isoformat() if rec and rec.responded_at else None,
        "sent": sent,
        "link": f"{rec.token}" if rec else None,
    }


@router.get("/recipients")
def list_recipients(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(None),
):
    """Admin view: accepted-abstract presenters who haven't registered, with
    their form/response status so the secretariat can send the form."""
    auth_dependency.secure_access("VIEW_ABSTRACTS", current_user["user_id"])
    presenters = _unregistered_presenters(db, event_id)
    return [_serialize_recipient(db, p) for p in presenters]


class SendFormBody(BaseModel):
    event_id: Optional[int] = None
    selected_emails: Optional[list] = None


@router.post("/send")
def send_attendance_forms(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    body: SendFormBody = None,
):
    """Generate a personal form link for each selected (or all) unregistered
    presenter and email it to them."""
    auth_dependency.secure_access("VIEW_ABSTRACTS", current_user["user_id"])

    event_id = (body or SendFormBody()).event_id
    selected_emails = (body or SendFormBody()).selected_emails
    selected_set = (
        {e.strip().lower() for e in selected_emails} if selected_emails else None
    )

    presenters = _unregistered_presenters(db, event_id)
    recipients = []
    for p in presenters:
        email = p["email"]
        if selected_set is not None and email not in selected_set:
            continue
        rec = (
            db.query(AttendanceFormResponse)
            .filter(
                AttendanceFormResponse.email == email,
                AttendanceFormResponse.event_id == p["event_id"],
                AttendanceFormResponse.deleted_at == None,
            )
            .first()
        )
        if not rec:
            rec = AttendanceFormResponse(
                event_id=p["event_id"],
                email=email,
                firstname=p["firstname"],
                lastname=p["lastname"],
                abstract_title=p["abstract_title"],
                token=secrets.token_urlsafe(24),
            )
            db.add(rec)
            db.commit()
            db.refresh(rec)
        recipients.append({**p, "token": rec.token, "firstname": p["firstname"] or "Presenter"})

    sent_by_user_id = current_user["user_id"]

    import utils.mailer_util as mailer_util
    from models.models import EmailTemplate as EmailTemplateModel
    from jinja2 import Template as Jinja2Template

    db_tpl = (
        db.query(EmailTemplateModel)
        .filter_by(template_key="attendance_confirmation_form")
        .first()
    )

    jobs = []
    for r in recipients:
        firstname = r["firstname"]
        event_name = r["event_name"]
        form_link = f"{mailer_util.CLIENT_ORIGIN}/#/attendance-form/{r['token']}"
        subject = f"Confirm Your Attendance for {event_name}"

        render_vars = dict(
            subject=subject,
            firstname=firstname,
            event_name=event_name,
            abstract_title=r["abstract_title"],
            form_link=form_link,
            year=mailer_util.YEAR,
        )
        try:
            if db_tpl and db_tpl.body_html:
                email_body = Jinja2Template(db_tpl.body_html).render(**render_vars)
            else:
                file_tpl = mailer_util.templates.get_template(
                    "attendance_form_template.html"
                )
                email_body = file_tpl.render(**render_vars)
        except Exception:
            email_body = (
                f"<p>Dear {firstname},</p>"
                f"<p>We noticed you haven't registered for <strong>{event_name}</strong>. "
                f"Please confirm whether you will still attend so we can plan the programme accordingly.</p>"
                f"<p><a href=\"{form_link}\" style=\"display:inline-block;padding:12px 28px;"
                f"background-color:rgb(254,80,103);color:#ffffff;text-decoration:none;"
                f"border-radius:8px;font-weight:600;\">Confirm Attendance</a></p>"
                f"<p>ECSACONM Events Team</p>"
            )

        jobs.append(
            {
                "recipient_email": r["email"],
                "subject": subject,
                "email_body": email_body,
                "email_type": "attendance_form",
                "sent_by_user_id": sent_by_user_id,
            }
        )

    forms_sent = len(jobs)
    if jobs:
        background_tasks.add_task(mailer_util.send_bulk_emails, jobs)

    return {
        "sent": forms_sent,
        "message": f"Attendance-confirmation forms queued for {forms_sent} presenter(s).",
        "forms_sent": forms_sent,
    }


@router.get("/form/{token}")
def get_attendance_form(token: str, db: Session = Depends(get_db)):
    """Public, no-auth: fetch the form details for a presenter's personal link."""
    rec = (
        db.query(AttendanceFormResponse)
        .options(joinedload(AttendanceFormResponse.event))
        .filter(
            AttendanceFormResponse.token == token,
            AttendanceFormResponse.deleted_at == None,
        )
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Form link is invalid or has expired.")
    return {
        "firstname": rec.firstname,
        "lastname": rec.lastname,
        "email": rec.email,
        "event_name": rec.event.event if rec.event else "ECSACONM Event",
        "abstract_title": rec.abstract_title,
        "already_responded": rec.response is not None,
        "response": rec.response,
    }


class SubmitFormBody(BaseModel):
    response: str


@router.post("/form/{token}")
def submit_attendance_form(token: str, body: SubmitFormBody, db: Session = Depends(get_db)):
    """Public, no-auth: record the presenter's attendance decision."""
    rec = (
        db.query(AttendanceFormResponse)
        .filter(
            AttendanceFormResponse.token == token,
            AttendanceFormResponse.deleted_at == None,
        )
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Form link is invalid or has expired.")

    response = (body.response or "").strip().lower()
    if response not in ("attending", "not_attending"):
        raise HTTPException(status_code=400, detail="Invalid response.")

    rec.response = response
    from datetime import datetime, timezone
    rec.responded_at = datetime.now(timezone.utc)
    db.commit()
    return {
        "message": "Thank you! Your response has been recorded.",
        "response": rec.response,
        "event_name": rec.event.event if rec.event else "ECSACONM Event",
    }


@router.get("/responses")
def list_responses(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(None),
    responded: str = Query(None),  # "yes" | "no"
):
    """Admin view: every form response for an event, for programme planning."""
    auth_dependency.secure_access("VIEW_ABSTRACTS", current_user["user_id"])
    q = db.query(AttendanceFormResponse).options(
        joinedload(AttendanceFormResponse.event)
    ).filter(AttendanceFormResponse.deleted_at == None)
    if event_id:
        q = q.filter(AttendanceFormResponse.event_id == event_id)
    if responded == "yes":
        q = q.filter(AttendanceFormResponse.response != None)
    elif responded == "no":
        q = q.filter(AttendanceFormResponse.response == None)
    records = q.order_by(AttendanceFormResponse.created_at.desc()).all()

    return {
        "data": [
            {
                "id": r.id,
                "event_id": r.event_id,
                "event_name": r.event.event if r.event else "ECSACONM Event",
                "firstname": r.firstname,
                "lastname": r.lastname,
                "email": r.email,
                "abstract_title": r.abstract_title,
                "response": r.response,
                "responded_at": r.responded_at.isoformat() if r.responded_at else None,
                "link": f"{r.token}",
            }
            for r in records
        ],
        "total": len(records),
    }