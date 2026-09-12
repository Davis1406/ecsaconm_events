import io
import math
from datetime import timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user
from models.models import Registration, User, Event, UserProfile, ParticipationRole

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


class RegistrationUpdateSchema(BaseModel):
    title: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    country_id: Optional[int] = None
    address: Optional[str] = None
    designation: Optional[str] = None
    organisation: Optional[str] = None
    participation_role: Optional[str] = None


def get_auth_dep(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


def _render_payment_reminder(subject_tpl, body_html_tpl, firstname, event_name, days_left, deadline):
    """Render the payment-reminder subject + body exactly as a send would, so
    the UI preview and the mailed email always match. ``subject_tpl`` may be
    None (falls back to the default subject) and ``body_html_tpl`` may be None
    (falls back to the file template)."""
    import utils.mailer_util as mailer_util
    from jinja2 import Template as Jinja2Template

    render_vars = dict(
        subject="",
        firstname=firstname,
        event_name=event_name,
        days_left=days_left,
        deadline=deadline,
        info_email="info@ecsaconm.org",
        cc_email="admission@cosecsa.org",
        year=mailer_util.YEAR,
    )
    # Subject supports both {days_left} and {{ days_left }} placeholder styles.
    subject = subject_tpl or "Payment Reminder: {days_left} day(s) left"
    for k, v in render_vars.items():
        if k == "subject":
            continue
        subject = subject.replace("{{ " + k + " }}", str(v)).replace(
            "{{" + k + "}}", str(v)
        ).replace("{" + k + "}", str(v))
    render_vars["subject"] = subject

    try:
        if body_html_tpl:
            body_html = Jinja2Template(body_html_tpl).render(**render_vars)
        else:
            file_tpl = mailer_util.templates.get_template("payment_reminder_template.html")
            body_html = file_tpl.render(**render_vars)
    except Exception:
        body_html = (
            f"<p>Dear {render_vars['firstname']},</p>"
            f"<p>You have <strong>{render_vars['days_left']} day(s)</strong> left to pay for "
            f"<strong>{render_vars['event_name']}</strong>. Payment is required to confirm your availability.</p>"
            f"<p>If you have already paid, please share your proof of payment with "
            f"{render_vars['info_email']} and copy {render_vars['cc_email']}.</p>"
            f"<p>ECSACONM Events Team</p>"
        )
    return subject, body_html


def _serialize_reg(r: Registration) -> dict:
    user = r.user
    profile = user.user_profile[0] if user.user_profile else None
    return {
        "id": r.id,
        "event_id": r.event_id,
        "event": r.events.event if r.events else None,
        "user_id": r.user_id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "phone": user.phone,
        "title": profile.title if profile else "",
        "organisation": profile.organisation if profile else "",
        "country": profile.country.country if profile and profile.country else "",
        "country_id": profile.country_id if profile else None,
        "address": profile.address if profile else "",
        "designation": profile.designation if profile else "",
        "participation_role": r.participation_role.name if r.participation_role else "",
        "paid": r.is_paid,
        "payment_proof": r.payment_proof,
        "registered_at": r.registered_at,
    }


@router.get("/participant_status/{registration_id}")
def participant_status(registration_id: int, db: Session = Depends(get_db)):
    from models.models import EventAttendance, Payment
    registration = (
        db.query(Registration)
        .options(
            joinedload(Registration.user),
            joinedload(Registration.payment),
            joinedload(Registration.event_attendance),
        )
        .filter(Registration.id == registration_id)
        .first()
    )
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    user = registration.user
    payment = registration.payment
    attendance_records = registration.event_attendance
    attendance_dates = [att.attendance_date.date() for att in attendance_records]

    return {
        "registration_id": registration.id,
        "participation_role": (
            registration.participation_role.name
            if registration.participation_role
            else None
        ),
        "paid": registration.is_paid,
        "user": {
            "id": user.id,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "phone": user.phone,
            "email": user.email,
        },
        "payment": (
            {
                "id": payment.id if payment else None,
                "amount": getattr(payment, "amount", None),
                "status": getattr(payment, "status", None),
                "paid_at": getattr(payment, "paid_at", None),
            }
            if payment
            else None
        ),
        "attendance": {
            "count": len(attendance_records),
            "dates": attendance_dates,
        },
    }


@router.get("/")
async def list_registrations(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10),
    search: str = Query(default=""),
    paid: str = Query(default="all"),
    proof: str = Query(default="all"),
    ids_only: bool = Query(default=False),
):
    auth_dependency.secure_access("VIEW_REGISTRATIONS", current_user["user_id"])

    q = (
        db.query(Registration)
        .join(Registration.user)
        .options(
            joinedload(Registration.user).joinedload(User.user_profile),
            joinedload(Registration.events),
        )
        .filter(Registration.deleted_at == None)
    )

    if event_id:
        q = q.filter(Registration.event_id == event_id)

    if paid != "all":
        q = q.filter(Registration.is_paid if paid == "true" else ~Registration.is_paid)

    if proof != "all":
        if proof == "with":
            q = q.filter(Registration.payment_proof.isnot(None))
        elif proof == "without":
            q = q.filter(Registration.payment_proof.is_(None))
        elif proof == "pending":
            q = q.filter(
                Registration.payment_proof.isnot(None),
                ~Registration.is_paid,
            )

    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                User.firstname.ilike(term),
                User.lastname.ilike(term),
                User.email.ilike(term),
                User.phone.ilike(term),
            )
        )

    total = q.count()
    if ids_only:
        # Lightweight mode used by "Select all N across pages" — return every
        # matching registration id without the per-row joins/payload.
        ids = [r.id for r in q.order_by(Registration.registered_at.desc()).all()]
        return {"total": total, "ids": ids}

    registrations = q.order_by(Registration.registered_at.desc()).offset(skip).limit(limit).all()
    pages = math.ceil(total / limit) if limit else 1

    return {
        "pages": pages,
        "total": total,
        "data": [_serialize_reg(r) for r in registrations],
    }


class BulkPaymentSchema(BaseModel):
    registration_ids: list[int]
    paid: bool


@router.post("/bulk_payment")
async def bulk_update_payment(
    data: BulkPaymentSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    """Bulk verify / un-verify payment for a set of registrations."""
    # ADMIN_DASHBOARD still bypasses this check; anyone entrusted with
    # VIEW_REGISTRATIONS (e.g. the Finance role) can also manage registration
    # payment status, matching their attendance-management access.
    auth_dependency.secure_access("VIEW_REGISTRATIONS", current_user["user_id"])
    if not data.registration_ids:
        raise HTTPException(status_code=400, detail="No registrations selected")

    regs = (
        db.query(Registration)
        .filter(Registration.id.in_(data.registration_ids), Registration.deleted_at == None)
        .all()
    )
    for r in regs:
        r.paid = data.paid
    db.commit()
    return {"updated": len(regs), "paid": data.paid}


class SendPaymentRemindersSchema(BaseModel):
    event_id: Optional[int] = None
    deadline: Optional[str] = None  # ISO date e.g. 2026-09-14
    registration_ids: Optional[list] = None


class ReminderPreviewSchema(BaseModel):
    event_id: Optional[int] = None
    deadline: Optional[str] = None  # ISO date e.g. 2026-09-14
    subject: Optional[str] = None   # working-copy subject (or use the template)
    body_html: Optional[str] = None # working-copy body (or use the template)


@router.post("/send_payment_reminders")
async def send_payment_reminders(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    body: SendPaymentRemindersSchema = None,
):
    """Email unpaid registrations a payment reminder with a countdown to the
    configured deadline, telling them to pay to confirm availability (or share
    proof if they've already paid). Uses the admin-editable `payment_reminder`
    email template."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])

    body = body or SendPaymentRemindersSchema()
    event_id = body.event_id
    selected_ids = set(body.registration_ids or [])
    deadline_str = body.deadline

    # Resolve deadline: explicit body value > stored system setting > event start
    from models.models import SystemSetting
    setting = (
        db.query(SystemSetting).filter(SystemSetting.key == "payment_deadline").first()
    )
    stored_deadline = setting.value if setting and setting.value else None
    resolved_deadline = deadline_str or stored_deadline

    # Persist the deadline so future sends reuse it
    if deadline_str:
        if setting:
            setting.value = deadline_str
        else:
            db.add(SystemSetting(key="payment_deadline", value=deadline_str))
        db.commit()

    def _parse_date(s):
        from datetime import date
        try:
            return date.fromisoformat(str(s)[:10])
        except Exception:
            return None

    q = (
        db.query(Registration)
        .join(Registration.user)
        .options(
            joinedload(Registration.user).joinedload(User.user_profile),
            joinedload(Registration.events),
        )
        .filter(Registration.deleted_at == None, ~Registration.is_paid)
    )
    if event_id:
        q = q.filter(Registration.event_id == event_id)
    if selected_ids:
        q = q.filter(Registration.id.in_(selected_ids))

    regs = q.order_by(Registration.registered_at.desc()).all()
    recipients = []
    for r in regs:
        user = r.user
        if not user or not user.email:
            continue
        # Determine deadline per registration: body/setting, else this event's start
        deadline_date = _parse_date(resolved_deadline)
        if not deadline_date and r.events and r.events.start_date:
            deadline_date = r.events.start_date.date()
        if not deadline_date:
            continue
        from datetime import date as _date
        days_left = max(0, (deadline_date - _date.today()).days)
        recipients.append(
            {
                "email": user.email,
                "firstname": user.firstname or "Participant",
                "event_name": r.events.event if r.events else "ECSACONM Event",
                "days_left": days_left,
                "deadline": deadline_date.isoformat(),
            }
        )

    sent_by_user_id = current_user["user_id"]

    import utils.mailer_util as mailer_util
    from models.models import EmailTemplate as EmailTemplateModel

    db_tpl = (
        db.query(EmailTemplateModel)
        .filter_by(template_key="payment_reminder")
        .first()
    )

    jobs = []
    for r in recipients:
        subject, email_body = _render_payment_reminder(
            db_tpl.subject if db_tpl else None,
            db_tpl.body_html if db_tpl else None,
            r["firstname"], r["event_name"], r["days_left"], r["deadline"],
        )
        jobs.append(
            {
                "recipient_email": r["email"],
                "subject": subject,
                "email_body": email_body,
                "email_type": "payment_reminder",
                "sent_by_user_id": sent_by_user_id,
            }
        )

    sent = len(jobs)
    if jobs:
        background_tasks.add_task(mailer_util.send_bulk_emails, jobs)

    return {
        "sent": sent,
        "deadline": resolved_deadline,
        "message": f"Payment reminders queued for {sent} unpaid registration(s).",
        "reminders_sent": sent,
    }


@router.post("/send_payment_reminders/preview")
async def preview_payment_reminders(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    body: ReminderPreviewSchema = None,
):
    """Render the payment-reminder subject + body exactly as they would be sent
    (same Jinja templates, same deadline resolution) using a sample recipient,
    so the UI can show an accurate preview without sending anything."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])

    body = body or ReminderPreviewSchema()
    from datetime import date as _date

    def _parse_date(s):
        try:
            return _date.fromisoformat(str(s)[:10])
        except Exception:
            return None

    from models.models import SystemSetting
    setting = (
        db.query(SystemSetting).filter(SystemSetting.key == "payment_deadline").first()
    )
    stored_deadline = setting.value if setting and setting.value else None
    deadline_date = _parse_date(body.deadline or stored_deadline)

    event_name = "ECSACONM Scientific Conference"
    if body.event_id:
        event = db.query(Event).filter(Event.id == body.event_id).first()
        if event:
            event_name = event.event
            if not deadline_date and event.start_date:
                deadline_date = event.start_date.date()

    if not deadline_date:
        deadline_date = _date.today() + timedelta(days=14)

    days_left = max(0, (deadline_date - _date.today()).days)

    from models.models import EmailTemplate as EmailTemplateModel
    db_tpl = (
        db.query(EmailTemplateModel)
        .filter_by(template_key="payment_reminder")
        .first()
    )

    subject, body_html = _render_payment_reminder(
        body.subject or (db_tpl.subject if db_tpl else None),
        body.body_html or (db_tpl.body_html if db_tpl else None),
        "Jane Presenter", event_name, days_left, deadline_date.isoformat(),
    )

    return {
        "subject": subject,
        "body_html": body_html,
        "days_left": days_left,
        "deadline": deadline_date.isoformat(),
    }


@router.get("/export")
async def export_registrations(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(default=None),
    paid: str = Query(default="all"),
    proof: str = Query(default="all"),
    search: str = Query(default=""),
):
    auth_dependency.secure_access("EXPORT_REGISTRATIONS", current_user["user_id"])

    q = (
        db.query(Registration)
        .join(Registration.user)
        .options(
            joinedload(Registration.user).joinedload(User.user_profile),
            joinedload(Registration.events),
            joinedload(Registration.payment),
        )
        .filter(Registration.deleted_at == None)
    )

    if event_id:
        q = q.filter(Registration.event_id == event_id)

    if paid != "all":
        q = q.filter(Registration.is_paid if paid == "true" else ~Registration.is_paid)

    if proof != "all":
        if proof == "with":
            q = q.filter(Registration.payment_proof.isnot(None))
        elif proof == "without":
            q = q.filter(Registration.payment_proof.is_(None))
        elif proof == "pending":
            q = q.filter(
                Registration.payment_proof.isnot(None),
                ~Registration.is_paid,
            )

    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                User.firstname.ilike(term),
                User.lastname.ilike(term),
                User.email.ilike(term),
            )
        )

    registrations = q.order_by(Registration.registered_at.desc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Registrations"

    header_fill = PatternFill("solid", start_color="0095B6")
    alt_fill = PatternFill("solid", start_color="E8F4F8")
    header_font = Font(name="Arial", bold=True, color="FFFFFF", size=10)
    body_font = Font(name="Arial", size=10)
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    headers = [
        "#", "Title", "First Name", "Last Name", "Email", "Phone",
        "Organisation", "Country", "Event", "Participation Role",
        "Paid", "Registered At",
    ]
    ws.row_dimensions[1].height = 22
    for ci, h in enumerate(headers, 1):
        cell = ws.cell(1, ci, h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
    ws.freeze_panes = "A2"

    for ri, r in enumerate(registrations, 2):
        use_fill = alt_fill if ri % 2 == 0 else PatternFill("solid", start_color="FFFFFF")
        user = r.user
        profile = user.user_profile[0] if user.user_profile else None
        row = [
            r.id,
            profile.title if profile else "",
            user.firstname,
            user.lastname,
            user.email,
            user.phone,
            profile.organisation if profile else "",
            profile.country.country if profile and profile.country else "",
            r.events.event if r.events else "",
            r.participation_role.name if r.participation_role else "",
            "Yes" if r.is_paid else "No",
            r.registered_at.strftime("%d %b %Y %H:%M") if r.registered_at else "",
        ]
        for ci, val in enumerate(row, 1):
            cell = ws.cell(ri, ci, val)
            cell.font = body_font
            cell.fill = use_fill
            cell.alignment = left

    col_widths = [6, 8, 18, 18, 30, 16, 28, 20, 36, 18, 8, 18]
    for ci, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(ci)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    filename = "registrations_export.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/{registration_id}")
async def get_registration(
    registration_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("VIEW_REGISTRATIONS", current_user["user_id"])

    reg = (
        db.query(Registration)
        .options(
            joinedload(Registration.user).joinedload(User.user_profile),
            joinedload(Registration.events),
        )
        .filter(Registration.id == registration_id, Registration.deleted_at == None)
        .first()
    )
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    return _serialize_reg(reg)


@router.put("/{registration_id}")
async def update_registration(
    registration_id: int,
    data: RegistrationUpdateSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("VIEW_REGISTRATIONS", current_user["user_id"])

    reg = (
        db.query(Registration)
        .options(
            joinedload(Registration.user).joinedload(User.user_profile),
        )
        .filter(Registration.id == registration_id, Registration.deleted_at == None)
        .first()
    )
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    user = reg.user

    # Update user core fields
    if data.firstname is not None:
        user.firstname = data.firstname
    if data.lastname is not None:
        user.lastname = data.lastname
    if data.phone is not None:
        user.phone = data.phone

    # Update user profile fields
    profile = user.user_profile[0] if user.user_profile else None
    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    if data.title is not None:
        profile.title = data.title
    if data.country_id is not None:
        profile.country_id = data.country_id
    if data.address is not None:
        profile.address = data.address
    if data.designation is not None:
        profile.designation = data.designation
    if data.organisation is not None:
        profile.organisation = data.organisation

    # Update participation role on registration
    if data.participation_role is not None:
        try:
            reg.participation_role = ParticipationRole(data.participation_role)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid participation_role: {data.participation_role}",
            )

    db.commit()
    db.refresh(reg)

    return _serialize_reg(reg)
