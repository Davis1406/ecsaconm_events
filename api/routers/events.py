import math, os
import uuid
import shutil
import textwrap
from fastapi.responses import StreamingResponse
from openpyxl import Workbook, load_workbook
from io import BytesIO
from typing import Literal
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from fastapi import status, HTTPException, File, Form, UploadFile
from typing import Annotated
from core.database import get_db
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from dependencies.auth_dependency import Auth
from dependencies.dependency import Dependency
from dependencies.auth_dependency import get_current_user, get_optional_current_user
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from models.models import Event, User, Registration, Document, Link, Payment, UserProfile, Country, UserPhoto, UserRole
from models.models import ParticipationRole, PaymentStatus, PaymentMethod, Abstract, AbstractAuthor
from utils.mailer_util import hash_password
from schemas.events_space import EventSchema, EventUpdateSchema, RegistrationSchema, LinkSchema, SendReceiptSchema, AddParticipantSchema, OnsiteRegistrationSchema
from utils.receipt_generator import generate_receipt_pdf
from utils.mailer_util import send_email_with_attachment
from fastapi import BackgroundTasks
from PIL import Image, ImageOps
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A5, A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
import qrcode
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
import unicodedata
import re
import urllib.parse


router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_dependency(db: Session = Depends(get_db)) -> Dependency:
    return Dependency(db)


def get_auth_dependency(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


CLIENT_ORIGIN = os.getenv("CLIENT_ORIGIN", "unknown_origin")


EVENT_DOCUMENT_DIR = "uploads/event/documents"
if not os.path.exists(EVENT_DOCUMENT_DIR):
    os.makedirs(EVENT_DOCUMENT_DIR)

EVENT_BANNER_DIR = "uploads/event/banners"
if not os.path.exists(EVENT_BANNER_DIR):
    os.makedirs(EVENT_BANNER_DIR)

ORG_UNIT_LOGO_DIR = "uploads/org_unit/logos"
if not os.path.exists(ORG_UNIT_LOGO_DIR):
    os.makedirs(ORG_UNIT_LOGO_DIR)


def get_object(id: int, db: Session, model):
    data = db.query(model).filter(model.id == id).first()
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"{model.__name__} with ID {id} does not exist or has been deleted",
        )
    return data


def sanitize_filename(name: str) -> str:
    # Normalize to remove accents
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    # Replace spaces and remove non-word characters
    name = re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "_")
    return name


# Define mapping of participation_role keys to display names
PARTICIPATION_ROLE_MAP = {
    "secretariat": "ECSA-HC secretariat",
    "moh": "Country delegate (from Ministry of Health)",
    "member_state": "Participant from ECSA Member States",
    "other_africa": "Participant from other African countries",
    "world": "Participant from the Rest of the World",
    "student": "Student",
    "exibitor": "Sponsor/Exhibitor",
}

# Badge "category bar" labels — keep in sync with
# web_vue/src/utils/badgeCategory.js::formatBadgeCategory().
# Member States, Other Africa and general Participant registrations are all
# printed on the badge simply as "Delegate"; everything else keeps its own
# distinct label.
_BADGE_DELEGATE_ROLE_KEYS = {"member_state", "other_africa", "participant"}
_BADGE_ROLE_LABELS = {
    "world": "International",
    "student": "Student",
    "exhibitor": "Exhibitor",
    "exibitor": "Exhibitor",
    "secretariat": "Secretariat",
    "delegate": "Delegate",
    "presenter": "Presenter",
    "speaker": "Speaker",
    "sponsor": "Sponsor",
    "moderator": "Moderator",
    "moh": "Ministry of Health",
    "media": "Media",
    "usher": "Usher",
    "member": "Member",
}


def format_badge_category(role_key: str) -> str:
    key = (role_key or "").strip().lower()
    if not key:
        return "Delegate"
    if key in _BADGE_DELEGATE_ROLE_KEYS:
        return "Delegate"
    if key in _BADGE_ROLE_LABELS:
        return _BADGE_ROLE_LABELS[key]
    return " ".join(w.capitalize() for w in re.split(r"[_\s]+", key) if w)


# Category-bar gradient per role — (dark, light, edge) hex triplets. Delegates
# (and everything without an override) keep the navy bar; staff/event teams get
# their own colour so badges are instantly distinguishable at a glance.
_BADGE_CATEGORY_GRADIENTS = {
    "secretariat": ("#14532d", "#166534", "#22c55e"),   # green
    "media": ("#78350f", "#92400e", "#f59e0b"),         # amber
    "exhibitor": ("#134e4a", "#0f766e", "#14b8a6"),     # teal
    "usher": ("#1e3a8a", "#1d4ed8", "#3b82f6"),         # blue
}
_BADGE_DEFAULT_GRADIENT = ("#173a4b", "#1d4659", "#2b5d73")  # navy


def badge_category_gradient(role_key: str) -> tuple:
    """Return the (dark, light, edge) hex triplets for a role's category bar."""
    key = (role_key or "").strip().lower()
    if key in _BADGE_DELEGATE_ROLE_KEYS:
        key = "delegate"
    return _BADGE_CATEGORY_GRADIENTS.get(key, _BADGE_DEFAULT_GRADIENT)


def convert_png_to_rgb(path):
    """Load a badge logo for ReportLab, preserving any alpha channel.

    Callers draw with ``mask="auto"``, which embeds a PNG's transparency as a
    soft mask — so transparent areas let the circle behind the logo show
    through instead of painting a white box (the ECSACONM logo sits on a solid
    red circle, where a flattened white background is very visible).
    """
    img = Image.open(path)
    if img.mode == "P":
        img = img.convert("RGBA")
    return ImageReader(img)


def normalize_event_name(name: str) -> str:
    return (
        name.replace("ᵗʰ", "th")
        .replace("ˢᵗ", "st")
        .replace("ⁿᵈ", "nd")
        .replace("ʳᵈ", "rd")
    )


@router.get("/active/")
async def get_active_events(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = 10,
    search: str = "",
):
    """Public endpoint — no auth required. Returns upcoming/active events."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    search_filter = or_(
        Event.event.ilike(f"%{search}%"),
        Event.theme.ilike(f"%{search}%"),
        Event.description.ilike(f"%{search}%"),
    )

    filters = [Event.deleted_at.is_(None), Event.end_date >= now]
    if search:
        filters.insert(0, search_filter)

    events_query = (
        db.query(Event)
        .options(joinedload(Event.org_unit))
        .filter(*filters)
        .order_by(Event.start_date.asc())
    )

    total_count = events_query.count()
    events = events_query.offset(skip).limit(limit).all()
    pages = math.ceil(total_count / limit) if total_count else 1

    return {
        "pages": pages,
        "total": total_count,
        "data": [
            {
                "id": e.id,
                "event": e.event,
                "theme": e.theme,
                "description": e.description,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "location": e.location,
                "banner_image": e.banner_image,
                "org_unit_id": e.org_unit_id,
                "country_id": e.country_id,
            }
            for e in events
        ],
    }


@router.get("")
@router.get("/")
async def get_events(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    search: str = "",
):
    search_filter = or_(
        Event.event.ilike(f"%{search}%"),
        Event.theme.ilike(f"%{search}%"),
        Event.description.ilike(f"%{search}%"),
    )

    filters = [Event.deleted_at.is_(None)]
    if search:
        filters.insert(0, search_filter)

    all_events = (
        db.query(Event)
        .filter(*filters)
        .order_by(Event.start_date.desc())
        .with_entities(
            Event.id,
            Event.event,
            Event.start_date,
            Event.end_date,
            Event.location,
            Event.banner_image,
            Event.theme,
            Event.organizers,
            Event.org_unit_id,
            Event.country_id,
            Event.abstract_submission_open,
        )
        .all()
    )

    total_count = len(all_events)
    events = all_events[skip : skip + limit] if limit else all_events

    pages = math.ceil(total_count / limit) if limit else 1
    return {
        "pages": pages,
        "total": total_count,
        "data": [
            {
                "id": e.id,
                "event": e.event,
                "theme": e.theme,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "location": e.location,
                "banner_image": e.banner_image,
                "organizers": e.organizers,
                "org_unit_id": e.org_unit_id,
                "country_id": e.country_id,
                "abstract_submission_open": e.abstract_submission_open,
            }
            for e in events
        ],
    }


@router.post("/")
async def add_event(
    request: Request,
    event_schema: EventSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("ADD_EVENT", current_user["user_id"])

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user["user_id"],
        "ADD_EVENT",
        current_user["username"],
        client_ip,
        event_schema.event,
    )

    create_event_model = Event(
        org_unit_id=event_schema.org_unit_id,
        country_id=event_schema.country_id,
        user_id=current_user["user_id"],
        event=event_schema.event,
        theme=event_schema.theme,
        description=event_schema.description,
        location=event_schema.location,
        start_date=event_schema.start_date,
        end_date=event_schema.end_date,
        banner_image=event_schema.banner_image,
        organizers=event_schema.organizers,
        participation_info=event_schema.participation_info,
        logistics_info=event_schema.logistics_info,
        sponsors_info=event_schema.sponsors_info,
        abstract_submission_open=event_schema.abstract_submission_open,
    )

    db.add(create_event_model)
    db.commit()
    db.refresh(create_event_model)
    return {"id": create_event_model.id}


@router.get("/scan/{registration_id}")
async def scan_registration(
    registration_id: int,
    db: Session = Depends(get_db),
):
    """Public — called when a badge QR code is scanned."""
    from datetime import date
    from models.models import EventAttendance, UserProfile

    registration = (
        db.query(Registration)
        .options(
            joinedload(Registration.user).joinedload(User.user_profile).joinedload(UserProfile.country),
            joinedload(Registration.events),
        )
        .filter(Registration.id == registration_id)
        .first()
    )
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    user = registration.user
    event = registration.events
    profile = user.user_profile[0] if user and user.user_profile else None
    country = profile.country.country if profile and profile.country else None

    today = date.today()
    all_attendance = (
        db.query(EventAttendance)
        .filter(EventAttendance.registration_id == registration_id)
        .order_by(EventAttendance.attendance_date.desc())
        .all()
    )
    today_attendance = next(
        (a for a in all_attendance if (a.attendance_date or a.created_at).date() == today),
        None,
    )
    role_key = (
        registration.participation_role.name
        if hasattr(registration.participation_role, "name")
        else str(registration.participation_role)
    )
    return {
        "registration": {"id": registration.id, "paid": registration.is_paid, "participation_role": role_key},
        "participant": {
            "firstname": user.firstname if user else "",
            "lastname": user.lastname if user else "",
            "email": user.email if user else "",
            "title": profile.title if profile else "",
            "designation": profile.designation if profile else "",
            "organisation": profile.organisation if profile else "",
            "country": country,
        },
        "event": {
            "id": event.id if event else None,
            "event": event.event if event else "",
            "location": event.location if event else "",
            "start_date": str(event.start_date) if event and event.start_date else "",
            "end_date": str(event.end_date) if event and event.end_date else "",
            "theme": event.theme if event else "",
            "event_day": (
                (date.today() - event.start_date.date()).days + 1
                if event and event.start_date and (date.today() - event.start_date.date()).days >= 0
                else None
            ),
        },
        "attendance": {
            "registered_today": today_attendance is not None,
            "total_days": len(all_attendance),
            "records": [
                {"date": str(a.attendance_date.date() if a.attendance_date else a.created_at.date()), "id": a.id}
                for a in all_attendance
            ],
        },
    }


@router.post("/send_receipt/{registration_id}")
async def send_receipt(
    registration_id: int,
    body: SendReceiptSchema,
    background_tasks: BackgroundTasks,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    """Generate a PDF receipt and email it to the participant."""
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    participant = registration.user
    if not participant:
        raise HTTPException(status_code=404, detail="Participant user not found")

    event = db.query(Event).filter(Event.id == registration.event_id).first()
    profile = participant.user_profile[0] if participant.user_profile else None

    # Amount paid — prefer Payment record, fall back to 0
    payment = registration.payment
    amount_paid = float(payment.payment_amount) if payment and payment.payment_amount else 0.0

    # Direct file URLs
    base_url = os.getenv("BASE_URL", "http://localhost:8001")
    payment_proof_url = None
    if registration.payment_proof:
        proof = registration.payment_proof
        # If it's already an http URL, keep as-is; otherwise build file URL
        if proof.startswith("http"):
            payment_proof_url = proof
        else:
            payment_proof_url = f"{base_url}/{proof}"

    photo_url = None
    photo_record = db.query(UserPhoto).filter(
        UserPhoto.user_id == participant.id,
        UserPhoto.deleted_at == None,
    ).order_by(UserPhoto.id.desc()).first()
    if photo_record and photo_record.path:
        if photo_record.path.startswith("http"):
            photo_url = photo_record.path
        else:
            photo_url = f"{base_url}/{photo_record.path}"

    pdf_bytes = generate_receipt_pdf(
        registration_id=registration.id,
        firstname=participant.firstname or "",
        lastname=participant.lastname or "",
        title_prefix=profile.title if profile else "",
        event_name=event.event if event else "Conference Registration",
        participation_role=registration.participation_role,
        amount_paid=amount_paid,
        date=datetime.utcnow(),
        membership_status=body.membership_status,
        membership_arrears=body.membership_arrears,
        payment_proof_url=payment_proof_url,
        photo_url=photo_url,
    )

    receipt_no = f"{registration.id}{datetime.utcnow().strftime('%m%d%Y')}"
    filename = f"Receipt_{receipt_no}.pdf"
    event_name_safe = (event.event or "Conference").replace(" ", "_")[:40]
    subject = f"Receipt – {event_name_safe}"

    full_name = " ".join(filter(None, [
        profile.title if profile else "",
        participant.firstname or "",
        participant.lastname or "",
    ]))
    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;">
      <div style="background:#fe5067;padding:16px 24px;">
        <h2 style="color:white;margin:0;font-size:18px;">ECSACONM – Payment Receipt</h2>
      </div>
      <div style="padding:24px;border:1px solid #eee;">
        <p>Dear <b>{full_name}</b>,</p>
        <p>Please find attached your official payment receipt for the <b>{event.event if event else 'conference'}</b>.</p>
        <p>Receipt No: <b style="color:#c0392b;">{receipt_no}</b></p>
        {"<p>Payment Proof: <a href='" + payment_proof_url + "'>View / Download</a></p>" if payment_proof_url else ""}
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;">© All Rights Reserved, ECSACONM</p>
      </div>
    </div>
    """

    background_tasks.add_task(
        send_email_with_attachment,
        participant.email,
        subject,
        html_body,
        pdf_bytes,
        filename,
        "payment_receipt",
        user["user_id"],
    )

    return {"status": "sent", "receipt_no": receipt_no, "email": participant.email}


@router.get("/{event_id}")
async def get_event(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    current_user: Optional[dict] = Depends(get_optional_current_user),
    participant_skip: int = Query(default=0, ge=0),
    participant_limit: int = Query(default=25, ge=1, le=200),
    participant_filter: str = Query(default="all"),
    participant_search: str = Query(default=""),
    participant_sort: str = Query(default="registered_at"),
    participant_dir: str = Query(default="desc"),
):
    client_ip = dependency.request_ip(request)

    dependency.log_activity(
        1,
        "VIEW_EVENT",
        "None",
        client_ip,
        f"View event id {event_id} and associated permissions",
    )

    if event := get_object(event_id, db, Event):
        documents = event.documents or []
        links = event.links or []

        # Build a set of emails that are accepted abstract presenters for this event
        presenter_emails = set(
            row.email.strip().lower()
            for row in db.query(AbstractAuthor.email)
            .join(Abstract, AbstractAuthor.abstract_id == Abstract.id)
            .filter(
                Abstract.event_id == event_id,
                Abstract.deleted_at == None,
                Abstract.status == "accepted",
                AbstractAuthor.is_presenting == True,
                AbstractAuthor.email != None,
                AbstractAuthor.email != "",
            )
            .all()
            if row.email
        )

        # ── Determine the current user's access level ─────────────────────────
        # "none"   → not logged in
        # "unpaid" → logged in but no paid registration for this event
        # "paid"   → has a paid registration OR has admin/secretariat permission
        user_access = "none"
        # Whether this caller is allowed to see the full participant roster
        # (names, emails, phones, payment info). Anonymous/expired-token callers
        # (this endpoint is also used by the public registration/payment pages,
        # so auth here is intentionally optional) never get participant PII —
        # only users holding ADMIN_DASHBOARD or VIEW_EVENT do.
        can_view_participants = False
        if current_user:
            uid = current_user["user_id"]
            from models.models import UserRole, RolePermission, Permission as Perm
            granted_codes = {
                row[0]
                for row in db.query(Perm.permission_code)
                .join(RolePermission, Perm.id == RolePermission.permission_id)
                .join(UserRole, RolePermission.role_id == UserRole.role_id)
                .filter(UserRole.user_id == uid)
                .all()
            }
            is_admin = "ADMIN_DASHBOARD" in granted_codes
            can_view_participants = is_admin or "VIEW_EVENT" in granted_codes

            if is_admin:
                user_access = "paid"
            else:
                reg = db.query(Registration).filter(
                    Registration.user_id == uid,
                    Registration.event_id == event_id,
                    Registration.deleted_at == None,
                ).first()
                if reg and reg.is_paid:
                    user_access = "paid"
                else:
                    user_access = "unpaid"

        def visible(item_access_level):
            level = item_access_level or "public"
            if level == "public":
                return True
            if level == "registered":
                return user_access != "none"
            # "admin" (or anything else unrecognised) — staff only
            return can_view_participants

        # ── Participant roster (paginated + filterable) ───────────────────────
        # Loaded in batches so the event page renders fast instead of pulling
        # every participant (with all their joins) up front. Counts are computed
        # server-side so the stat strip / filter chips stay accurate across pages.
        reg_q = (
            db.query(Registration)
            .options(
                joinedload(Registration.user).joinedload(User.user_profile).joinedload(UserProfile.country),
                joinedload(Registration.user).joinedload(User.user_photo),
                joinedload(Registration.payment),
                joinedload(Registration.events),
            )
            .filter(Registration.event_id == event_id, Registration.deleted_at == None)
        )

        base_total = (
            db.query(Registration)
            .filter(Registration.event_id == event_id, Registration.deleted_at == None)
            .count()
        )
        paid_total = (
            db.query(Registration)
            .filter(
                Registration.event_id == event_id,
                Registration.deleted_at == None,
                Registration.is_paid,
            )
            .count()
        )
        proof_pending_total = (
            db.query(Registration)
            .filter(
                Registration.event_id == event_id,
                Registration.deleted_at == None,
                Registration.payment_proof.isnot(None),
                ~Registration.is_paid,
            )
            .count()
        )
        presenter_total = 0
        if presenter_emails:
            presenter_total = (
                db.query(Registration)
                .join(User, Registration.user_id == User.id)
                .filter(
                    Registration.event_id == event_id,
                    Registration.deleted_at == None,
                    User.email.in_(presenter_emails),
                )
                .count()
            )

        secretariat_total = (
            db.query(Registration)
            .filter(
                Registration.event_id == event_id,
                Registration.deleted_at == None,
                Registration.participation_role == ParticipationRole.secretariat,
            )
            .count()
        )
        badge_exported_total = (
            db.query(Registration)
            .filter(
                Registration.event_id == event_id,
                Registration.deleted_at == None,
                Registration.badge_exported_at.isnot(None),
            )
            .count()
        )

        filter_counts = {
            "all": base_total,
            "paid": paid_total,
            "unpaid": base_total - paid_total,
            "proof_pending": proof_pending_total,
            "presenters": presenter_total,
            "secretariat": secretariat_total,
            "badges_exported": badge_exported_total,
        }

        if participant_filter == "paid":
            reg_q = reg_q.filter(Registration.is_paid)
        elif participant_filter == "unpaid":
            reg_q = reg_q.filter(~Registration.is_paid)
        elif participant_filter == "proof_pending":
            reg_q = reg_q.filter(
                Registration.payment_proof.isnot(None),
                ~Registration.is_paid,
            )
        elif participant_filter == "secretariat":
            reg_q = reg_q.filter(
                Registration.participation_role == ParticipationRole.secretariat
            )
        elif participant_filter == "badges_exported":
            reg_q = reg_q.filter(Registration.badge_exported_at.isnot(None))

        needs_user_join = (
            (participant_filter == "presenters" and presenter_emails)
            or bool(participant_search)
        )
        if needs_user_join:
            reg_q = reg_q.join(User, Registration.user_id == User.id)
        if participant_filter == "presenters" and presenter_emails:
            reg_q = reg_q.filter(User.email.in_(presenter_emails))
        if participant_search:
            term = f"%{participant_search.strip()}%"
            reg_q = reg_q.filter(
                or_(
                    User.firstname.ilike(term),
                    User.lastname.ilike(term),
                    User.email.ilike(term),
                    User.phone.ilike(term),
                )
            )

        participants_total = reg_q.count()

        # Server-side sort. Related fields are ordered via correlated
        # scalar subqueries (a user can have several profile rows, so a plain
        # join would duplicate registrations and inflate the count).
        sort_key = (participant_sort or "registered_at").lower()
        sort_dir = "asc" if (participant_dir or "desc").lower() == "asc" else "desc"
        firstname_subq = (
            db.query(User.firstname)
            .filter(User.id == Registration.user_id)
            .scalar_subquery()
        )
        lastname_subq = (
            db.query(User.lastname)
            .filter(User.id == Registration.user_id)
            .scalar_subquery()
        )
        organisation_subq = (
            db.query(UserProfile.organisation)
            .filter(
                UserProfile.user_id == Registration.user_id,
                UserProfile.deleted_at == None,
            )
            .order_by(UserProfile.id.asc())
            .limit(1)
            .scalar_subquery()
        )
        country_subq = (
            db.query(Country.country)
            .join(UserProfile, UserProfile.country_id == Country.id)
            .filter(
                UserProfile.user_id == Registration.user_id,
                UserProfile.deleted_at == None,
            )
            .order_by(UserProfile.id.asc())
            .limit(1)
            .scalar_subquery()
        )
        sort_columns = {
            "name": (firstname_subq, lastname_subq),
            "institution": (organisation_subq,),
            "country": (country_subq,),
            "paid": (Registration.is_paid,),
            "registered_at": (Registration.registered_at,),
        }
        order_cols = sort_columns.get(sort_key, (Registration.registered_at,))
        order_by = [
            col.asc() if sort_dir == "asc" else col.desc() for col in order_cols
        ]
        # Stable tie-breaker so pagination doesn't shuffle equal rows.
        order_by.append(Registration.id.asc())

        registrations = (
            reg_q.order_by(*order_by)
            .offset(participant_skip)
            .limit(participant_limit)
            .all()
        )

        # The current user's own participation role (public pages), independent
        # of the participant page being viewed.
        my_role = None
        if current_user and user_access != "none":
            my_reg = db.query(Registration).filter(
                Registration.user_id == current_user["user_id"],
                Registration.event_id == event_id,
                Registration.deleted_at == None,
            ).first()
            my_role = my_reg.participation_role if my_reg else None

        return {
            "event": {
                "id": event.id,
                "event": event.event,
                "country_id": event.country_id,
                "country": event.country.country if event.country else None,
                "org_unit_id": event.org_unit_id,
                "org_unit": event.org_unit.name if event.org_unit else None,
                "org_unit_primary_color": event.org_unit.primary_color if event.org_unit else "#0095B6",
                "org_unit_secondary_color": event.org_unit.secondary_color if event.org_unit else "#F7941D",
                "org_unit_logo": event.org_unit.logo if event.org_unit else None,
                "user_id": event.user_id,
                "firstname": event.user.firstname if event.user else None,
                "lastname": event.user.lastname if event.user else None,
                "location": event.location,
                "theme": event.theme,
                "description": event.description,
                "start_date": event.start_date,
                "end_date": event.end_date,
                "banner_image": event.banner_image,
                "organizers": event.organizers,
                "participation_info": event.participation_info,
                "logistics_info": event.logistics_info,
                "sponsors_info": event.sponsors_info,
                "abstract_submission_open": event.abstract_submission_open,
                "participation_role": my_role,
                "user_access": user_access,
            },
            "participants_total": participants_total if can_view_participants else 0,
            "participants_total_all": base_total if can_view_participants else 0,
            "filter_counts": filter_counts if can_view_participants else {},
            "participants": [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "firstname": r.user.firstname if r.user else None,
                    "lastname": r.user.lastname if r.user else None,
                    "phone": r.user.phone if r.user else None,
                    "email": r.user.email if r.user else None,
                    "photo": (
                        r.user.user_photo[0].path
                        if r.user and r.user.user_photo and len(r.user.user_photo) > 0
                        else None
                    ),
                    "country_id": (
                        r.user.user_profile[0].country_id
                        if r.user and r.user.user_profile
                        else None
                    ),
                    "country": (
                        r.user.user_profile[0].country.country
                        if r.user and r.user.user_profile and r.user.user_profile[0].country
                        else None
                    ),
                    "title": (
                        r.user.user_profile[0].title
                        if r.user and r.user.user_profile
                        else None
                    ),
                    "designation": (
                        r.user.user_profile[0].designation
                        if r.user and r.user.user_profile
                        else None
                    ),
                    "participation_role": r.participation_role,
                    "organisation": (
                        r.user.user_profile[0].organisation
                        if r.user and r.user.user_profile
                        else None
                    ),
                    "paid": r.is_paid,
                    "payment_proof": getattr(r, "payment_proof", None),
                    "badge_exported_at": r.badge_exported_at,
                    "payment_amount": (
                        float(r.payment.payment_amount)
                        if r.payment and r.payment.payment_amount else 0
                    ),
                    "registered_at": r.registered_at,
                    "is_abstract_presenter": (
                        (r.user.email or "").strip().lower() in presenter_emails
                        if r.user else False
                    ),
                }
                for r in registrations
                if can_view_participants
            ],
            "documents": [
                {
                    "id": d.id,
                    "document_type": d.document_type,
                    "file_type": d.file_type,
                    "file_name": d.file_name,
                    "name": d.name,
                    "path": d.path,
                    "access_level": d.access_level,
                }
                for d in documents
                if visible(d.access_level)
            ],
            "links": [
                {
                    "id": l.id,
                    "name": l.name,
                    "link": l.link,
                    "access_level": l.access_level or "public",
                }
                for l in links
                if visible(l.access_level)
            ],
        }
    else:
        raise HTTPException(status_code=404, detail="event not found")


@router.put("/{event_id}")
async def update_event(
    request: Request,
    event_id: int,
    current_user: user_dependency,
    event_schema: EventUpdateSchema,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("UPDATE_EVENT", current_user["user_id"])

    client_ip = dependency.request_ip(request)

    dependency.log_activity(
        current_user["user_id"],
        "UPDATE_EVENT",
        current_user["username"],
        client_ip,
        f"Update event id {event_id}",
    )
    event_model = get_object(event_id, db, Event)

    event_model.org_unit_id = event_schema.org_unit_id
    event_model.country_id = event_schema.country_id
    event_model.user_id = current_user["user_id"]
    event_model.event = event_schema.event
    event_model.theme = event_schema.theme
    event_model.description = event_schema.description
    event_model.location = event_schema.location
    event_model.start_date = event_schema.start_date
    event_model.end_date = event_schema.end_date
    event_model.organizers = event_schema.organizers
    event_model.participation_info = event_schema.participation_info
    event_model.logistics_info = event_schema.logistics_info
    event_model.sponsors_info = event_schema.sponsors_info
    event_model.abstract_submission_open = event_schema.abstract_submission_open
    if event_schema.banner_image is not None:
        event_model.banner_image = event_schema.banner_image

    db.commit()
    db.refresh(event_model)
    return event_schema


@router.delete("/{event_id}")
async def delete_event(
    request: Request,
    event_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("DELETE_EVENT", current_user["user_id"])

    dependency.cascade_soft_delete_recursive(Event, event_id)

    client_ip = dependency.request_ip(request)
    event = get_object(event_id, db, Event)

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user["user_id"],
        "DELETE_EVENT",
        current_user["username"],
        client_ip,
        f"Delete event id {event_id} event {event.event}",
    )
    return {"detail": "event Successfully deleted"}


@router.get("/registration/{registration_id}")
async def get_registration_details(
    request: Request,
    registration_id: int,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
):
    client_ip = dependency.request_ip(request)

    dependency.log_activity(
        1,
        "VIEW_REGISTRATION",
        "None",
        client_ip,
        f"View registration ID {registration_id}",
    )

    registration = get_object(registration_id, db, Registration)
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    user = db.query(User).filter(User.id == registration.user_id).first()
    event = db.query(Event).filter(Event.id == registration.event_id).first()

    return {
        "registration": {
            "id": registration.id,
            "user_id": registration.user_id,
            "event_id": registration.event_id,
            "participation_role": registration.participation_role.name,
            "paid": registration.is_paid,
            "created_at": registration.created_at,
            "updated_at": registration.updated_at,
        },
        "user": (
            {
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "phone": user.phone,
            }
            if user
            else None
        ),
        "event": (
            {
                "id": event.id,
                "event": event.event,
                "location": event.location,
                "start_date": event.start_date,
                "end_date": event.end_date,
            }
            if event
            else None
        ),
    }


@router.post("/registration/{user_id}")
async def event_registration(
    request: Request,
    user_id: int,
    registration_schema: RegistrationSchema,
    # current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    # auth_dependency: Auth = Depends(get_auth_dependency),
):
    # user = db.query(User).filter(User.id == user_id).first()
    # client_ip = dependency.request_ip(request)

    # dependency.log_activity(
    #     1,
    #     "EVENT_REGISTRATION",
    #     user.email,
    #     client_ip,
    #     f"Event ID: {registration_schema.event_id}",
    # )

    # Check for existing registration
    existing_registration = (
        db.query(Registration)
        .filter(
            Registration.user_id == user_id,
            Registration.event_id == registration_schema.event_id,
        )
        .first()
    )

    if existing_registration:
        # Update existing registration
        existing_registration.participation_role = (
            registration_schema.participation_role
        )
        db.commit()
        db.refresh(existing_registration)
        return {
            "message": "Registration updated successfully",
            "registration_id": existing_registration.id,
        }

    # Create new registration
    new_registration = Registration(
        user_id=user_id,
        event_id=registration_schema.event_id,
        participation_role=registration_schema.participation_role,
    )
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    return {
        "message": "Registration successful",
        "registration_id": new_registration.id,
    }


@router.post("/{event_id}/participants")
async def add_event_participant(
    request: Request,
    event_id: int,
    data: AddParticipantSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    """Admin: quickly add a single participant to an event.

    Finds or creates the user account by email, fills in their profile, and
    creates (or restores) their event registration. New accounts get the
    standard temporary password and the default "User" role.
    """
    auth_dependency.secure_access("BULK_UPLOAD", current_user["user_id"])

    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    try:
        role = ParticipationRole(data.participation_role)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid participation_role: {data.participation_role}",
        )

    email = (data.email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        phone = (data.phone or "").strip()
        if not phone:
            base = f"9{abs(hash(email)) % 10**9:09d}"[:20]
            phone, suffix = base, 0
            while db.query(User).filter(User.phone == phone).first():
                suffix += 1
                phone = f"{base[:18]}{suffix:02d}"
        user = User(
            firstname=(data.firstname or "").strip(),
            lastname=(data.lastname or "").strip(),
            email=email,
            phone=phone,
            hashed_password=hash_password("Ecsaconm@2025"),
            verified=True,
        )
        db.add(user)
        db.flush()
        db.add(UserRole(user_id=user.id, role_id=6))
    else:
        if data.firstname:
            user.firstname = data.firstname.strip()
        if data.lastname:
            user.lastname = data.lastname.strip()
        if data.phone:
            user.phone = data.phone.strip()

    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user.id, UserProfile.deleted_at == None)
        .first()
    )
    if not profile:
        profile = UserProfile(
            user_id=user.id, title="", middle_name="", gender="", position="",
            organisation="", profession="", designation="", certificate_name="", address="",
        )
        db.add(profile)
    if data.title is not None:
        profile.title = data.title
    if data.designation is not None:
        profile.designation = data.designation
    if data.organisation is not None:
        profile.organisation = data.organisation
    if data.country_id is not None:
        profile.country_id = data.country_id

    reg = (
        db.query(Registration)
        .filter(Registration.user_id == user.id, Registration.event_id == event_id)
        .first()
    )
    if not reg:
        reg = Registration(
            user_id=user.id, event_id=event_id, participation_role=role, paid=False
        )
        db.add(reg)
    else:
        reg.deleted_at = None
        reg.participation_role = role

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not add participant: {e.orig}")

    db.refresh(reg)
    return {
        "message": "Participant added",
        "registration_id": reg.id,
        "user_id": user.id,
    }


@router.post("/{event_id}/onsite_registration")
async def onsite_register_participant(
    event_id: int,
    data: OnsiteRegistrationSchema,
    db: Session = Depends(get_db),
):
    """Public, no-login walk-in check-in for people who have already paid at
    the venue — reached by scanning a printed QR at the Finance desk. Email
    is optional; the phone number is the identifying field, and a placeholder
    @onsite.ecsaconm.org email is generated when none is given so the User
    row's NOT NULL/unique email constraint still holds.
    """
    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    try:
        role = ParticipationRole(data.participation_role or "delegate")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid participation_role: {data.participation_role}",
        )

    phone = (data.phone or "").strip()
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number is required")

    email = (data.email or "").strip().lower()
    generated_email = not email
    if generated_email:
        digits = re.sub(r"\D", "", phone) or uuid.uuid4().hex[:9]
        email = f"{digits}@onsite.ecsaconm.org"

    # Walk-ins are identified by phone first (that's the field guaranteed to
    # be filled in); only fall back to email if a real one was supplied.
    user = db.query(User).filter(User.phone == phone).first()
    if not user and not generated_email:
        user = db.query(User).filter(User.email == email).first()

    if not user:
        # Placeholder emails are built from phone digits — vanishingly
        # unlikely to collide, but guard against it instead of a 500.
        while db.query(User).filter(User.email == email).first():
            email = f"{email.split('@')[0]}{uuid.uuid4().hex[:4]}@onsite.ecsaconm.org"
        user = User(
            firstname=(data.firstname or "").strip(),
            lastname=(data.lastname or "").strip(),
            email=email,
            phone=phone,
            hashed_password=hash_password("Ecsaconm@2025"),
            verified=True,
        )
        db.add(user)
        db.flush()
        db.add(UserRole(user_id=user.id, role_id=6))
    else:
        if data.firstname:
            user.firstname = data.firstname.strip()
        if data.lastname:
            user.lastname = data.lastname.strip()

    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user.id, UserProfile.deleted_at == None)
        .first()
    )
    if not profile:
        profile = UserProfile(
            user_id=user.id, title="", middle_name="", gender="", position="",
            organisation="", profession="", designation="", certificate_name="", address="",
        )
        db.add(profile)
    if data.title is not None:
        profile.title = data.title
    if data.designation is not None:
        profile.designation = data.designation
    if data.organisation is not None:
        profile.organisation = data.organisation
    if data.country_id is not None:
        profile.country_id = data.country_id

    reg = (
        db.query(Registration)
        .filter(Registration.user_id == user.id, Registration.event_id == event_id)
        .first()
    )
    if not reg:
        # Onsite = already paid at the venue by definition.
        reg = Registration(user_id=user.id, event_id=event_id, participation_role=role, paid=True)
        db.add(reg)
    else:
        reg.deleted_at = None
        reg.participation_role = role
        reg.paid = True

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not complete registration: {e.orig}")

    db.refresh(reg)
    return {
        "message": "Onsite registration complete",
        "registration_id": reg.id,
        "user_id": user.id,
        "email": user.email,
        "generated_email": generated_email,
    }


@router.delete("/registration/{event_id}")
async def event_deregistration(
    request: Request,
    event_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    client_ip = dependency.request_ip(request)

    dependency.log_activity(
        1,
        "EVENT_DEREGISTER",
        "None",
        client_ip,
        f"Deregister event id {event_id}",
    )

    existing_registration = (
        db.query(Registration)
        .filter(
            Registration.user_id == current_user["user_id"],
            Registration.event_id == event_id,
        )
        .first()
    )

    try:
        # First: delete any payment (if exists)
        existing_payment = (
            db.query(Payment)
            .filter(Payment.registration_id == existing_registration.id)
            .first()
        )
        if existing_payment:
            db.delete(existing_payment)
            db.flush()  # flush ensures DB sees the delete before the next delete

        # Now delete the registration
        db.delete(existing_registration)
        db.commit()

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user event registration",
        ) from error


PAYMENT_RECEIPT_DIR = "uploads/payment_receipts"
if not os.path.exists(PAYMENT_RECEIPT_DIR):
    os.makedirs(PAYMENT_RECEIPT_DIR)


@router.delete("/deregister_participant/{registration_id}")
async def admin_deregister_participant(
    request: Request,
    registration_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    """Admin-only: deregister any participant by registration ID."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])

    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    try:
        # Delete attendance records
        from models.models import EventAttendance
        db.query(EventAttendance).filter(
            EventAttendance.registration_id == registration.id
        ).delete(synchronize_session=False)
        db.flush()

        # Delete payment record
        existing_payment = (
            db.query(Payment).filter(Payment.registration_id == registration.id).first()
        )
        if existing_payment:
            db.delete(existing_payment)
            db.flush()

        db.delete(registration)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deregister participant",
        ) from error

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user["user_id"],
        "ADMIN_DEREGISTER",
        current_user["username"],
        client_ip,
        f"Admin deregistered registration ID {registration_id}",
    )
    return {"detail": "Participant successfully deregistered"}


@router.post("/upload_payment_proof/{event_id}")
async def upload_payment_proof(
    event_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    file: UploadFile = File(None),
    payment_method: str = Form(default="bank_transfer"),
    payment_reference: str = Form(default=""),
    payment_amount: float = Form(default=0.0),
):
    """User uploads proof of payment for their registration."""
    from models.models import PaymentMethod as PM, PaymentStatus
    from datetime import datetime, timezone

    registration = db.query(Registration).filter(
        Registration.user_id == current_user["user_id"],
        Registration.event_id == event_id,
        Registration.deleted_at == None,
    ).first()

    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    try:
        file_path = None
        if file and file.filename:
            ext = os.path.splitext(file.filename)[1]
            unique_name = f"proof_{registration.id}_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(PAYMENT_RECEIPT_DIR, unique_name)
            with open(file_path, "wb+") as f:
                f.write(await file.read())
            registration.payment_proof = file_path

        # Map frontend payment_method string to enum
        method_map = {
            "bank_transfer": PM.BANK_TRANSFER,
            "mobile_money": PM.MPESA,
            "cash": PM.CASH,
            "card": PM.CARD,
        }
        method_enum = method_map.get(payment_method.lower(), PM.BANK_TRANSFER)

        # Create or update Payment record
        existing_payment = db.query(Payment).filter(
            Payment.registration_id == registration.id
        ).first()
        if existing_payment:
            existing_payment.payment_method = method_enum
            existing_payment.payment_reference = payment_reference or "N/A"
            existing_payment.payment_amount = payment_amount or 0
            existing_payment.payment_status = PaymentStatus.PENDING
            if file_path:
                existing_payment.payment_receipt = file_path
        else:
            new_payment = Payment(
                registration_id=registration.id,
                payment_date=datetime.now(timezone.utc),
                payment_method=method_enum,
                payment_reference=payment_reference or "N/A",
                payment_amount=payment_amount or 0,
                payment_status=PaymentStatus.PENDING,
                payment_receipt=file_path,
            )
            db.add(new_payment)

        db.commit()

        return JSONResponse(content={"status": "success", "payment_proof": file_path})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/verify_payment/{registration_id}")
async def verify_payment(
    request: Request,
    registration_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    """Admin verifies a participant's payment, setting paid=True."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])

    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    registration.paid = True
    db.commit()

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user["user_id"],
        "VERIFY_PAYMENT",
        current_user["username"],
        client_ip,
        f"Verified payment for registration ID {registration_id}",
    )
    return {"detail": "Payment verified successfully"}


@router.put("/unverify_payment/{registration_id}")
async def unverify_payment(
    request: Request,
    registration_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    """Admin un-verifies a participant's payment, setting paid=False."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])

    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    registration.paid = False
    db.commit()

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user["user_id"],
        "UNVERIFY_PAYMENT",
        current_user["username"],
        client_ip,
        f"Un-verified payment for registration ID {registration_id}",
    )
    return {"detail": "Payment un-verified successfully"}


@router.post("/upload_document/")
async def upload_document(
    user: user_dependency,
    file: UploadFile = File(...),
    file_name: str = Form(...),
    doc_type: str = Form(...),
    access_level: str = Form(...),
    event_id: int = Form(...),
    db: Session = Depends(get_db),
):
    try:
        unique_dir = os.path.join(
            EVENT_DOCUMENT_DIR,
            f"{event_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
        )
        os.makedirs(unique_dir, exist_ok=True)
        file_path = os.path.join(unique_dir, file.filename)
        with open(file_path, "wb+") as file_object:
            file_object.write(await file.read())

        event_document_model = Document(
            event_id=event_id,
            document_type=doc_type,
            file_type=file.content_type,
            file_name=file.filename,
            name=file_name,
            path=file_path,
            access_level=access_level,
        )
        db.add(event_document_model)
        db.commit()
        db.refresh(event_document_model)

        return JSONResponse(
            content={
                "status": "success",
                "message": f"File '{file.filename}' uploaded to '{unique_dir}'",
                "file_path": file_path,
            },
            status_code=200,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/upload_banner/{event_id}")
async def upload_banner(
    event_id: int,
    user: user_dependency,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        raw = await file.read()
        # Downscale + recompress banners (max 1920px wide, progressive JPEG ~82)
        # so multi-MB uploads don't slow down the public pages.
        try:
            from PIL import Image
            img = Image.open(BytesIO(raw))
            if img.width > 1920:
                img = img.resize((1920, int(img.height * 1920 / img.width)), Image.LANCZOS)
            file_path = os.path.join(
                EVENT_BANNER_DIR, f"{event_id}_{uuid.uuid4().hex[:8]}.jpg"
            )
            img.convert("RGB").save(
                file_path, "JPEG", quality=82, optimize=True, progressive=True
            )
        except Exception:
            # Not a parseable image — keep the original file as-is
            ext = os.path.splitext(file.filename)[1]
            file_path = os.path.join(
                EVENT_BANNER_DIR, f"{event_id}_{uuid.uuid4().hex[:8]}{ext}"
            )
            with open(file_path, "wb+") as f:
                f.write(raw)

        # Remove the previous banner file so orphans don't pile up
        old_path = event.banner_image
        event.banner_image = file_path
        db.commit()
        if old_path and old_path != file_path and os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

        return JSONResponse(content={"status": "success", "banner_image": file_path})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_document/{document_id}")
async def delete_document(
    request: Request,
    document_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("DELETE_EVENT", current_user["user_id"])

    document = get_object(document_id, db, Document)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    document_folder = os.path.dirname(document.path)
    if os.path.exists(document_folder):
        try:
            shutil.rmtree(document_folder)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete folder: {str(e)}"
            )
    else:
        raise HTTPException(status_code=404, detail="Folder not found on disk")

    db.delete(document)
    db.commit()

    return {"status": "success", "message": f"Document and folder deleted successfully"}


def _format_document_type(doc_type) -> str:
    label = doc_type.value if hasattr(doc_type, "value") else str(doc_type or "")
    return {
        "ProgrammeBooklet": "Programme Booklet",
        "Presentation": "Presentation",
        "Photo": "Photo",
        "Advert": "Advert",
        "Guidelines": "Guidelines",
        "Other": "Document",
    }.get(label, "Document")


def _wrap_by_width(text, font_name, font_size, max_width):
    """Greedy word-wrap: split `text` into lines that each fit `max_width`
    at the given font. A single word wider than max_width is kept whole
    (better to overflow slightly than to break a word mid-letter)."""
    words = text.split()
    if not words:
        return []
    lines, cur = [], words[0]
    for w in words[1:]:
        trial = f"{cur} {w}"
        if stringWidth(trial, font_name, font_size) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def _fit_lines(text, font_name, max_width, start_size, min_size=12, max_lines=3):
    """Pick the largest font size (down to min_size) at which `text` word-wraps
    into at most `max_lines` lines that all fit max_width — so a long event/
    document title shrinks and wraps instead of running off the page edge."""
    size = start_size
    lines = _wrap_by_width(text, font_name, size, max_width)
    while size > min_size and (
        len(lines) > max_lines or any(stringWidth(l, font_name, size) > max_width for l in lines)
    ):
        size -= 1
        lines = _wrap_by_width(text, font_name, size, max_width)
    return lines, size


def _render_qr_flyer(c, event_name, label, title_text, instruction, file_url, logo_left=None, logo_right=None):
    """Draw a one-page A4 flyer: ECSA/ECSACONM logos, event name, a coloured
    label, a title line, an instruction line, a large QR code linking to
    `file_url`, and the raw URL as a fallback. Shared by the per-document QR
    (label = document type, title = document name) and the onsite
    registration QR (label = "ONSITE REGISTRATION", title = a short prompt)."""
    W, H = A4

    RED = (220 / 255.0, 50 / 255.0, 75 / 255.0)          # rgb(220,50,75)
    PINK = (254 / 255.0, 80 / 255.0, 103 / 255.0)        # rgb(254,80,103)
    GRAY_800 = (31 / 255.0, 41 / 255.0, 55 / 255.0)
    GRAY_500 = (107 / 255.0, 114 / 255.0, 128 / 255.0)

    # Top / bottom accent bars
    c.setFillColorRGB(*PINK)
    c.rect(0, H - 10 * mm, W, 10 * mm, fill=1, stroke=0)
    c.setFillColorRGB(*RED)
    c.rect(0, 0, W, 6 * mm, fill=1, stroke=0)

    # ECSA / ECSACONM logos, pinned to the outer margins just below the top
    # bar — same circle treatment as the badge PDF (ECSA: white w/ pink
    # border; right logo: solid brand-red circle).
    logos_reserved = 0
    if logo_left or logo_right:
        logo_d = 26 * mm
        margin = 24 * mm
        left_cx = margin + logo_d / 2
        right_cx = W - margin - logo_d / 2
        logo_cy = H - 10 * mm - 6 * mm - logo_d / 2
        img_size = logo_d - 4 * mm

        if logo_left:
            c.saveState()
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(*PINK)
            c.setLineWidth(1.2)
            c.circle(left_cx, logo_cy, logo_d / 2, fill=1, stroke=1)
            c.restoreState()
            c.drawImage(logo_left, left_cx - img_size / 2, logo_cy - img_size / 2, img_size, img_size,
                        preserveAspectRatio=True, mask="auto")

        if logo_right:
            c.saveState()
            c.setFillColorRGB(*RED)
            c.circle(right_cx, logo_cy, logo_d / 2, fill=1, stroke=0)
            c.restoreState()
            c.drawImage(logo_right, right_cx - img_size / 2, logo_cy - img_size / 2, img_size, img_size,
                        preserveAspectRatio=True, mask="auto")

        logos_reserved = 6 * mm + logo_d + 8 * mm  # gap + logo + gap before the text block

    event_name = (event_name or "").strip()
    qr_size = 130 * mm
    pad = 7 * mm
    text_max_width = W - 40 * mm  # 20mm margin either side

    heading_font, title_font = "Helvetica-Bold", "Helvetica-Bold"
    heading_lines, heading_size = ([], 22)
    if event_name:
        heading_lines, heading_size = _fit_lines(event_name, heading_font, text_max_width, 22, min_size=14, max_lines=3)
    title_lines, title_size = _fit_lines(title_text, title_font, text_max_width, 19, min_size=13, max_lines=2)

    # Line heights in points (font size * a 1.25 leading factor).
    heading_line_h = heading_size * 1.25
    label_h = 10 * mm
    instruction_h = 10 * mm
    title_line_h = title_size * 1.25
    gap_before_qr = 8 * mm
    card_side = qr_size + pad * 2
    footer_gap = 12 * mm
    footer_h = 14 * mm

    heading_block_h = (heading_line_h * len(heading_lines) + 4 * mm) if heading_lines else 0
    title_block_h = title_line_h * len(title_lines)
    block_h = heading_block_h + label_h + instruction_h + title_block_h + gap_before_qr + card_side + footer_gap + footer_h

    usable_top = H - 16 * mm - logos_reserved
    usable_bottom = 6 * mm
    top = usable_bottom + (usable_top - usable_bottom + block_h) / 2
    top = min(top, usable_top)  # never draw text under the logos

    if heading_lines:
        c.setFillColorRGB(*GRAY_800)
        c.setFont(heading_font, heading_size)
        for line in heading_lines:
            c.drawCentredString(W / 2, top, line)
            top -= heading_line_h
        top -= 4 * mm

    c.setFillColorRGB(*RED)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(W / 2, top, label.upper())
    top -= label_h

    c.setFillColorRGB(*GRAY_500)
    c.setFont("Helvetica", 13)
    c.drawCentredString(W / 2, top, instruction)
    top -= instruction_h

    c.setFillColorRGB(*GRAY_800)
    c.setFont(title_font, title_size)
    for line in title_lines:
        c.drawCentredString(W / 2, top, line)
        top -= title_line_h
    top -= gap_before_qr

    qr = qrcode.make(file_url)
    qr_buf = BytesIO()
    qr.save(qr_buf, format="PNG")
    qr_buf.seek(0)

    qr_x = (W - qr_size) / 2
    qr_y = top - qr_size

    border_tint = tuple(0.75 * ch + 0.25 for ch in PINK)  # PINK lightened ~75% toward white
    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(*border_tint)
    c.setLineWidth(1.2)
    c.roundRect(qr_x - pad, qr_y - pad, qr_size + 2 * pad, qr_size + 2 * pad, 6 * mm, fill=1, stroke=1)
    c.drawImage(ImageReader(qr_buf), qr_x, qr_y, qr_size, qr_size)
    top = qr_y - footer_gap

    c.setFillColorRGB(*GRAY_500)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, top, "ECSACONM Events — events.ecsaconm.org")
    top -= 6 * mm
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(W / 2, top, file_url)


@router.get("/documents/{document_id}/qr")
async def get_document_qr_flyer(
    document_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    """A4 flyer PDF with a QR code pointing straight at the uploaded document,
    so secretariat can print and hand it out / post it at the venue."""
    document = get_object(document_id, db, Document)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    event = db.query(Event).filter(Event.id == document.event_id).first()

    base_url = os.getenv("BASE_URL", "http://localhost:8001")
    path = document.path
    file_url = path if path.startswith("http") else f"{base_url}/{path}"

    logo_left = convert_png_to_rgb("assets/logo_left.png")
    logo_right = convert_png_to_rgb("assets/logo.png")
    doc_title = document.name or document.file_name or "Document"

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _render_qr_flyer(
        c,
        getattr(event, "event", None),
        _format_document_type(document.document_type),
        doc_title,
        "Scan with your phone camera to open:",
        file_url,
        logo_left,
        logo_right,
    )
    c.showPage()
    c.save()
    buffer.seek(0)

    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", document.name or document.file_name or f"document_{document.id}").strip("_") or f"document_{document.id}"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{safe_name}_QR.pdf"'},
    )


@router.get("/{event_id}/onsite_registration/qr")
async def get_onsite_registration_qr_flyer(
    event_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    """A4 flyer PDF with a QR code linking to this event's public onsite
    registration form, for Finance to print and use at the venue desk."""
    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    file_url = f"{CLIENT_ORIGIN}/#/onsite-registration/{event_id}"

    logo_left = convert_png_to_rgb("assets/logo_left.png")
    logo_right = convert_png_to_rgb("assets/logo.png")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _render_qr_flyer(
        c,
        getattr(event, "event", None),
        "Onsite Registration",
        "Register a Walk-in Participant",
        "Finance: scan to register participants who have paid at the venue:",
        file_url,
        logo_left,
        logo_right,
    )
    c.showPage()
    c.save()
    buffer.seek(0)

    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", getattr(event, "event", None) or f"event_{event_id}").strip("_") or f"event_{event_id}"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{safe_name}_Onsite_Registration_QR.pdf"'},
    )


@router.get("/{event_id}/onsite_registration/qr_image")
async def get_onsite_registration_qr_image(
    event_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    """Just the raw QR code as a PNG (no flyer chrome) — for an inline
    on-page preview; the full printable flyer is at .../onsite_registration/qr."""
    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    file_url = f"{CLIENT_ORIGIN}/#/onsite-registration/{event_id}"
    qr = qrcode.make(file_url)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.get("/{event_id}/registration/qr")
async def get_online_registration_qr_flyer(
    event_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    """A4 flyer PDF with a QR code linking to this event's public online
    registration form — print/share to drive self-service sign-ups."""
    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    file_url = f"{CLIENT_ORIGIN}/#/register/{event_id}"

    logo_left = convert_png_to_rgb("assets/logo_left.png")
    logo_right = convert_png_to_rgb("assets/logo.png")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _render_qr_flyer(
        c,
        getattr(event, "event", None),
        "Online Registration",
        "Register for This Event",
        "Scan with your phone camera to register online:",
        file_url,
        logo_left,
        logo_right,
    )
    c.showPage()
    c.save()
    buffer.seek(0)

    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", getattr(event, "event", None) or f"event_{event_id}").strip("_") or f"event_{event_id}"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{safe_name}_Registration_QR.pdf"'},
    )


@router.get("/{event_id}/registration/qr_image")
async def get_online_registration_qr_image(
    event_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    """Just the raw QR code as a PNG (no flyer chrome) — for an inline
    on-page preview; the full printable flyer is at .../registration/qr."""
    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    file_url = f"{CLIENT_ORIGIN}/#/register/{event_id}"
    qr = qrcode.make(file_url)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.post("/add_link/")
async def add_link(
    request: Request,
    link_schema: LinkSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user["user_id"],
        "ADD_EVENT",
        current_user["username"],
        client_ip,
        link_schema.event_id,
    )

    create_event_link_model = Link(
        event_id=link_schema.event_id,
        name=link_schema.name,
        link=str(link_schema.link),
        access_level=link_schema.access_level or "public",
    )

    db.add(create_event_link_model)
    db.commit()
    return link_schema


@router.put("/update_link/{link_id}")
async def update_link(
    request: Request,
    link_id: int,
    current_user: user_dependency,
    link_schema: LinkSchema,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("UPDATE_EVENT", current_user["user_id"])

    client_ip = dependency.request_ip(request)

    dependency.log_activity(
        current_user["user_id"],
        "UPDATE_EVENT",
        current_user["username"],
        client_ip,
        f"Update event id {link_id}",
    )
    link_model = get_object(link_id, db, Link)

    link_model.name = link_schema.name
    link_model.link = str(link_schema.link)

    db.commit()
    db.refresh(link_model)
    return link_schema


@router.delete("/delete_link/{link_id}")
async def delete_link(
    request: Request,
    link_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("DELETE_EVENT", current_user["user_id"])

    dependency.hard_delete(Link, link_id)

    client_ip = dependency.request_ip(request)
    link = get_object(link_id, db, Link)

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user["user_id"],
        "DELETE_EVENT",
        current_user["username"],
        client_ip,
        f"Delete event id {link} event {link.name}",
    )
    return {"detail": "link Successfully deleted"}


# ── Bulk import participants from Excel ────────────────────────────────────────

# ── Google Drive download helper (used during bulk import) ─────────────────────
import re as _re, hashlib as _hashlib, mimetypes as _mimetypes, io as _io, time as _time

_DRIVE_ID_RE = _re.compile(r"[?&/]id=([a-zA-Z0-9_-]+)|/d/([a-zA-Z0-9_-]+)")

def _extract_drive_id(url: str):
    m = _DRIVE_ID_RE.search(url or "")
    if m:
        return m.group(1) or m.group(2)
    return None

def _drive_download(url: str, dest_dir: str, filename_stem: str):
    """Try to download a Google Drive file. Returns local relative path or None."""
    file_id = _extract_drive_id(url)
    if not file_id:
        return None
    token_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "token.json")
    if not os.path.exists(token_path):
        return None   # no credentials cached — skip download, keep URL

    try:
        from google.oauth2.credentials import Credentials as GCreds
        from google.auth.transport.requests import Request as GRequest
        from googleapiclient.discovery import build as gbuild
        from googleapiclient.http import MediaIoBaseDownload

        creds = GCreds.from_authorized_user_file(token_path, ["https://www.googleapis.com/auth/drive.readonly"])
        if creds.expired and creds.refresh_token:
            creds.refresh(GRequest())

        service = gbuild("drive", "v3", credentials=creds)
        meta = service.files().get(fileId=file_id, fields="mimeType").execute()
        mime = meta.get("mimeType", "application/octet-stream")

        ext_map = {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif",
                   "image/webp": "webp", "application/pdf": "pdf"}
        ext = ext_map.get(mime) or (_mimetypes.guess_extension(mime) or ".bin").lstrip(".")

        request = service.files().get_media(fileId=file_id)
        buf = _io.BytesIO()
        dl = MediaIoBaseDownload(buf, request, chunksize=4 * 1024 * 1024)
        done = False
        while not done:
            _, done = dl.next_chunk()

        os.makedirs(dest_dir, exist_ok=True)
        uid = _hashlib.md5(file_id.encode()).hexdigest()[:8]
        fname = f"{filename_stem}_{uid}.{ext}"
        full_path = os.path.join(dest_dir, fname)
        with open(full_path, "wb") as fh:
            fh.write(buf.getvalue())

        # return a relative path (from api root)
        abs_api = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.relpath(full_path, abs_api)
    except Exception:
        return None   # fall back to storing the URL

# Maps Excel "Participation Category" text → ParticipationRole enum value
_ROLE_IMPORT_MAP = {
    "ecsacon members": "member_state",
    "ecsaconm members": "member_state",
    "member state": "member_state",
    "member_state": "member_state",
    "participant": "participant",
    "student": "student",
    "exhibitor": "exhibitor",
    "speaker": "speaker",
    "presenter": "presenter",
    "delegate": "delegate",
    "sponsor": "sponsor",
    "moderator": "moderator",
    "secretariat": "secretariat",
    "other africa": "other_africa",
    "international": "world",
    "moh": "moh",
    "ministry of health": "moh",
    "media": "media",
    "usher": "usher",
}


def _map_role(raw: str) -> ParticipationRole:
    key = (raw or "").strip().lower()
    value = _ROLE_IMPORT_MAP.get(key, "participant")
    return ParticipationRole(value)


def _normalize_header(h) -> str:
    return str(h or "").strip().lower()


def _detect_columns(headers: list) -> dict:
    """Return a dict mapping field name → column index (0-based)."""
    result = {}
    for i, h in enumerate(headers):
        n = _normalize_header(h)
        if "first" in n and "name" in n:
            result["firstname"] = i
        elif "last" in n and "name" in n:
            result["lastname"] = i
        elif n == "title":
            result["title"] = i
        elif "designation" in n:
            result["designation"] = i
        elif n == "country":
            result["country"] = i
        elif "email" in n:
            result.setdefault("email", i)           # first email column wins
        elif "telephone" in n or ("phone" in n and "code" not in n):
            result["phone"] = i
        elif "participation" in n or ("categor" in n and "membership" not in n):
            result["role"] = i
        elif "amount paid" in n:
            result["amount"] = i
        elif "full name" in n and ("certificate" in n or "appear" in n):
            result["certificate_name"] = i
        elif n == "address":
            result["address"] = i
        # Proof of payment — first occurrence wins
        elif "proof of payment" in n and "proof" not in result:
            result["proof"] = i
        # Badge / passport photo — first occurrence wins
        elif ("photo" in n or "badge" in n) and "photo" not in result:
            result["photo"] = i
        # Membership arrears status text (e.g. "Active member No Arrears")
        elif "membership arrears" in n and "arrears_status" not in result:
            result["arrears_status"] = i
        # Numeric arrears amount column (usually just labelled "arrears")
        elif n == "arrears" and "arrears_amount" not in result:
            result["arrears_amount"] = i
    return result


@router.post("/upload_participants/")
async def upload_participants(
    user: user_dependency,
    file: UploadFile = File(...),
    eventID: str = Form(...),
    db: Session = Depends(get_db),
):
    """Bulk-import participants from an Excel (.xlsx) or CSV file."""
    event_id = int(eventID)
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    contents = await file.read()

    # ── Parse the workbook ────────────────────────────────────────────────────
    try:
        wb = load_workbook(filename=BytesIO(contents), read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read Excel file: {e}")

    if not rows:
        raise HTTPException(status_code=400, detail="Excel file is empty")

    # Find header row — first row where we can detect at least email + firstname
    header_row_idx = 0
    col_map: dict = {}
    for idx, row in enumerate(rows):
        cm = _detect_columns(list(row))
        if "email" in cm and "firstname" in cm:
            header_row_idx = idx
            col_map = cm
            break

    if not col_map or "email" not in col_map:
        raise HTTPException(
            status_code=400,
            detail="Could not detect required columns. Expected: 'First Name', 'Last Name', 'Delegate Valid Email Address', etc.",
        )

    data_rows = rows[header_row_idx + 1:]

    created = updated = skipped = 0
    errors = []

    for row_num, row in enumerate(data_rows, start=header_row_idx + 2):
        def cell(field):
            idx = col_map.get(field)
            if idx is None:
                return None
            v = row[idx] if idx < len(row) else None
            return str(v).strip() if v is not None else None

        email = cell("email")
        if not email or "@" not in email:
            skipped += 1
            continue

        email = email.lower().strip()
        firstname = cell("firstname") or "Unknown"
        lastname = cell("lastname") or "Unknown"
        title_val = cell("title") or ""
        designation = cell("designation") or ""
        country_name = cell("country") or ""
        phone_raw = cell("phone") or ""
        role_raw = cell("role") or "participant"
        amount_raw = cell("amount")
        cert_name = cell("certificate_name") or ""

        # Sanitize phone: keep digits only, ensure non-empty
        phone_digits = "".join(c for c in phone_raw if c.isdigit())
        if not phone_digits:
            # Generate placeholder from email hash so it's unique
            import hashlib
            phone_digits = str(int(hashlib.md5(email.encode()).hexdigest()[:8], 16))[:12]

        # Resolve amount
        try:
            amount_paid = float(str(amount_raw).replace(",", "")) if amount_raw else 0.0
        except (ValueError, TypeError):
            amount_paid = 0.0

        # Resolve country
        country_obj = None
        if country_name:
            country_obj = (
                db.query(Country)
                .filter(Country.country.ilike(f"%{country_name}%"))
                .first()
            )

        # Resolve participation role
        try:
            role = _map_role(role_raw)
        except Exception:
            role = ParticipationRole.participant

        try:
            # ── Find or create User ───────────────────────────────────────────
            existing_user = db.query(User).filter(User.email == email).first()

            if existing_user:
                # Update name if blank
                if not existing_user.firstname or existing_user.firstname == "Unknown":
                    existing_user.firstname = firstname
                if not existing_user.lastname or existing_user.lastname == "Unknown":
                    existing_user.lastname = lastname
                user_obj = existing_user
                updated += 1
            else:
                # Check phone uniqueness — adjust if taken
                phone_candidate = phone_digits[:20]
                if db.query(User).filter(User.phone == phone_candidate).first():
                    import time
                    phone_candidate = phone_digits[:16] + str(int(time.time()))[-4:]

                user_obj = User(
                    firstname=firstname,
                    lastname=lastname,
                    email=email,
                    phone=phone_candidate,
                    hashed_password=hash_password("Ecsaconm@2025"),
                    verified=True,
                )
                db.add(user_obj)
                db.flush()  # get user_obj.id
                # Assign default "User" role (role_id=6)
                db.add(UserRole(user_id=user_obj.id, role_id=6))
                created += 1

            # ── Find or create UserProfile ────────────────────────────────────
            profile = db.query(UserProfile).filter(
                UserProfile.user_id == user_obj.id,
                UserProfile.deleted_at == None,
            ).first()

            if profile:
                if country_obj:
                    profile.country_id = country_obj.id
                if designation:
                    profile.designation = designation
                if title_val:
                    profile.title = title_val
                if cert_name:
                    profile.certificate_name = cert_name
            else:
                profile = UserProfile(
                    user_id=user_obj.id,
                    country_id=country_obj.id if country_obj else None,
                    title=title_val or '',
                    middle_name='',
                    gender='',
                    position='',
                    organisation='',
                    profession='',
                    designation=designation or '',
                    certificate_name=cert_name or '',
                    address='',
                )
                db.add(profile)

            # ── Find or create Registration ───────────────────────────────────
            reg = db.query(Registration).filter(
                Registration.user_id == user_obj.id,
                Registration.event_id == event_id,
            ).first()

            if reg:
                reg.participation_role = role
                if amount_paid > 0:
                    reg.paid = True
            else:
                reg = Registration(
                    user_id=user_obj.id,
                    event_id=event_id,
                    participation_role=role,
                    paid=amount_paid > 0,
                )
                db.add(reg)
                db.flush()

            # ── Create Payment record if paid ─────────────────────────────────
            if amount_paid > 0:
                reg.paid = True
                existing_payment = db.query(Payment).filter(
                    Payment.registration_id == reg.id
                ).first()
                if not existing_payment:
                    payment_rec = Payment(
                        registration_id=reg.id,
                        payment_date=datetime.utcnow(),
                        payment_method=PaymentMethod.BANK_TRANSFER,
                        payment_reference=f"IMPORT_{reg.id}",
                        payment_amount=amount_paid,
                        payment_status=PaymentStatus.COMPLETED,
                    )
                    db.add(payment_rec)
                else:
                    existing_payment.payment_amount = amount_paid
                    existing_payment.payment_status = PaymentStatus.COMPLETED

            # ── Save proof of payment (download Drive file if possible) ──────
            proof_url = cell("proof")
            if proof_url and proof_url.startswith("http"):
                local = _drive_download(
                    proof_url,
                    dest_dir="uploads/payment_receipts",
                    filename_stem=f"proof_{reg.id}",
                )
                reg.payment_proof = local if local else proof_url

            # ── Save address to profile ───────────────────────────────────────
            addr = cell("address")
            if addr and profile:
                profile.address = addr

            # ── Save badge photo (download Drive file if possible) ────────────
            photo_url = cell("photo")
            if photo_url and photo_url.startswith("http"):
                ts  = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                uid = _hashlib.md5(f"{user_obj.id}{ts}".encode()).hexdigest()[:8]
                folder = f"uploads/picture/profile_picture/{user_obj.id}_{ts}_{uid}"
                local = _drive_download(
                    photo_url,
                    dest_dir=folder,
                    filename_stem="profile",
                )
                save_path = local if local else photo_url
                existing_photo = db.query(UserPhoto).filter(
                    UserPhoto.user_id == user_obj.id,
                    UserPhoto.deleted_at == None,
                ).first()
                if existing_photo:
                    existing_photo.path = save_path
                else:
                    db.add(UserPhoto(user_id=user_obj.id, path=save_path))

            db.commit()

        except Exception as e:
            db.rollback()
            errors.append(f"Row {row_num} ({email}): {str(e)}")

    return {
        "status": "complete",
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors[:10],  # return first 10 errors max
        "total_processed": created + updated + skipped,
    }


@router.get("/{event_id}/participants/download")
async def download_event_participants(
    request: Request,
    event_id: int,
    current_user: user_dependency,
    paid: Literal["all", "true", "false"] = Query("all"),
    db: Session = Depends(get_db),
    dependency=Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    # Permission check
    auth_dependency.secure_access("VIEW_EVENT", current_user["user_id"])
    client_ip = dependency.request_ip(request)

    dependency.log_activity(
        current_user["user_id"],
        "DOWNLOAD_PARTICIPANTS",
        current_user["username"],
        client_ip,
        f"Downloaded participants for event {event_id} with filter paid={paid}",
    )

    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Collect participant details
    participants = []
    for reg in event.registrations:
        user = reg.user
        profile = user.user_profile[0] if user.user_profile else None
        country = profile.country.country if profile and profile.country else None
        organisation = profile.organisation if profile else None

        # Convert participation_role to string key (adjust this if ParticipationRole is Enum)
        role_key = (
            reg.participation_role.name
            if hasattr(reg.participation_role, "name")
            else str(reg.participation_role).lower()
        )

        participants.append(
            {
                "registration_id": reg.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "phone": user.phone,
                "title": profile.title if profile else "",
                "middle_name": profile.middle_name if profile else "",
                "gender": profile.gender if profile else "",
                "position": profile.position if profile else "",
                "organisation": organisation,
                "country": country,
                "participation_role": PARTICIPATION_ROLE_MAP.get(role_key, role_key),
                "paid": reg.is_paid,
                "registered_at": reg.registered_at,
            }
        )

    # Filter by paid status
    if paid != "all":
        is_paid = paid == "true"
        participants = [p for p in participants if p["paid"] == is_paid]

    if not participants:
        raise HTTPException(status_code=404, detail="No participants found")

    # Create Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Participants"

    headers = [
        "ID",
        "Title",
        "First Name",
        "Middle Name",
        "Last Name",
        "Gender",
        "Email",
        "Phone",
        "Organisation",
        "Position",
        "Country",
        "Participation Role",
        "Paid",
        "Registered At",
    ]
    ws.append(headers)

    for p in participants:
        ws.append(
            [
                p["registration_id"],
                p["title"],
                p["firstname"],
                p["middle_name"],
                p["lastname"],
                p["gender"],
                p["email"],
                p["phone"],
                p["organisation"] or "",
                p["position"],
                p["country"] or "",
                p["participation_role"],
                "Yes" if p["paid"] else "No",
                p["registered_at"].strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )

    # Stream response
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    safe_event_name = sanitize_filename(event.event)
    ascii_filename = f"{safe_event_name}_participants.xlsx"
    utf8_filename = urllib.parse.quote(ascii_filename)

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={ascii_filename}; filename*=UTF-8''{utf8_filename}"
        },
    )


@router.get("/with-registration/{user_id}")
@router.get("/with-registration/{user_id}/")
def list_events_with_user_registration(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # or your custom dependency
):
    # Get all events
    events = db.query(Event).all()

    # Get all registrations by the user
    user_regs = (
        db.query(Registration)
        .filter(Registration.user_id == user_id, Registration.deleted_at.is_(None))
        .all()
    )

    # Build a lookup dictionary for quick access: event_id -> registration
    reg_map = {reg.event_id: reg for reg in user_regs}

    # Construct result
    result = []
    for event in events:
        registration = reg_map.get(event.id)
        result.append(
            {
                "event": {
                    "id": event.id,
                    "title": event.event,
                    "theme": event.theme,
                    "description": event.description,
                    "start_date": event.start_date,
                    "end_date": event.end_date,
                    "location": event.location,
                    "country": event.country.country if event.country else None,
                    "org_unit": event.org_unit.name if event.org_unit else None,
                },
                "registered": bool(registration),
                "registration_details": (
                    {
                        "registration_id": registration.id,
                        "participation_role": registration.participation_role,
                        "paid": registration.is_paid,
                        "payment_status": "Paid" if registration.is_paid else "Not Paid",
                        "registered_at": registration.registered_at,
                    }
                    if registration
                    else None
                ),
            }
        )

    return result


def hex_to_rgb(hex_color: str):
    """Convert a hex color string like '#a02626' to a 0.0-1.0 RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i: i + 2], 16) / 255.0 for i in (0, 2, 4))


_BADGE_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]


def _badge_ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _format_badge_date_range(start_date, end_date) -> str:
    """Mirrors web_vue/src/utils/badgeEvent.js::formatBadgeDateRange()."""
    if not start_date:
        return ""
    start_day = _badge_ordinal(start_date.day)
    start_month = _BADGE_MONTHS[start_date.month - 1]
    if not end_date or start_date.date() == end_date.date():
        return f"{start_day} {start_month}, {start_date.year}"
    end_day = _badge_ordinal(end_date.day)
    end_month = _BADGE_MONTHS[end_date.month - 1]
    if (start_date.year, start_date.month) == (end_date.year, end_date.month):
        return f"{start_day} – {end_day} {end_month}, {end_date.year}"
    return f"{start_day} {start_month} – {end_day} {end_month}, {end_date.year}"


def _parse_badge_title(event_name: str) -> dict:
    """Mirrors web_vue/src/utils/badgeEvent.js::parseBadgeTitle().

    Splits an event title like "17th ECSACONM Biennial Scientific Conference
    & 8th Quadrennial General Assembly" into the header pieces the badge
    design uses: a leading ordinal + org name, a subtitle line, and an
    optional pill line.
    """
    name = (event_name or "").strip()
    if not name:
        return {"ordinal": "", "org": "ECSACONM", "subtitle": "", "pill": ""}
    m = re.match(r"^(\d+(?:st|nd|rd|th))\s+(\S+)\s*(.*)$", name, re.IGNORECASE)
    if not m:
        return {"ordinal": "", "org": name, "subtitle": "", "pill": ""}
    ordinal, org, rest = m.group(1), m.group(2), m.group(3)
    parts = [s.strip() for s in re.split(r"\s*&\s*|\s+and\s+", rest, flags=re.IGNORECASE) if s.strip()]
    return {
        "ordinal": ordinal,
        "org": org,
        "subtitle": parts[0] if len(parts) > 0 else "",
        "pill": parts[1] if len(parts) > 1 else "",
    }


def _interp_rgb(stops, t):
    """Linear-interpolate an RGB color at position t (0..1) across `stops`,
    a list of (position, (r,g,b)) pairs sorted by position."""
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return tuple(c0[i] + (c1[i] - c0[i]) * f for i in range(3))
    return stops[-1][1]


def _gradient_rect(c, x, y, w, h, stops, steps=48):
    """Approximate a left-to-right CSS linear-gradient with vertical bands."""
    band_w = w / steps + 0.6
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        c.setFillColorRGB(*_interp_rgb(stops, t))
        c.rect(x + (i / steps) * w, y, band_w, h, fill=True, stroke=False)


def _draw_diamond_pattern(c, x, y, w, h, color, tile, alpha=0.16):
    """Repeating outlined-diamond motif, mirrors the footer's SVG pattern."""
    c.saveState()
    clip = c.beginPath()
    clip.rect(x, y, w, h)
    c.clipPath(clip, stroke=0, fill=0)
    c.setStrokeColorRGB(*color)
    c.setStrokeAlpha(alpha)
    c.setLineWidth(0.4)
    half = tile / 2
    cols = int(w / tile) + 2
    rows = int(h / tile) + 2
    for row in range(-1, rows):
        for col in range(-1, cols):
            cx, cy = x + col * tile, y + row * tile
            d = c.beginPath()
            d.moveTo(cx, cy + half)
            d.lineTo(cx + half, cy)
            d.lineTo(cx, cy - half)
            d.lineTo(cx - half, cy)
            d.close()
            c.drawPath(d, fill=0, stroke=1)
    c.restoreState()


def _draw_calendar_icon(c, x, y, s, color):
    """Small calendar glyph; (x, y) is its bottom-left corner, s its width."""
    c.saveState()
    c.setStrokeColorRGB(*color)
    c.setLineWidth(0.35)
    body_h = s * 0.82
    c.roundRect(x, y, s, body_h, s * 0.12, fill=0, stroke=1)
    c.line(x, y + body_h * 0.62, x + s, y + body_h * 0.62)
    c.line(x + s * 0.22, y + body_h, x + s * 0.22, y + body_h + s * 0.22)
    c.line(x + s * 0.78, y + body_h, x + s * 0.78, y + body_h + s * 0.22)
    c.restoreState()


def _draw_pin_icon(c, cx, top_y, s, color):
    """Small map-pin glyph; (cx, top_y) is its top-center point, s its height."""
    c.saveState()
    c.setFillColorRGB(*color)
    r = s * 0.34
    circle_cy = top_y - r
    c.circle(cx, circle_cy, r, fill=1, stroke=0)
    tip = c.beginPath()
    tip.moveTo(cx - r * 0.85, circle_cy - r * 0.35)
    tip.lineTo(cx + r * 0.85, circle_cy - r * 0.35)
    tip.lineTo(cx, top_y - s)
    tip.close()
    c.drawPath(tip, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.circle(cx, circle_cy, r * 0.4, fill=1, stroke=0)
    c.restoreState()


def _draw_blob(c, cx, cy, r, color, peak=0.16, steps=26):
    """Soft-edged decorative blob. Concentric fills accumulate into a radial
    falloff, approximating the preview's blurred CSS circle."""
    c.saveState()
    c.setFillColorRGB(*color)
    step_alpha = 1 - (1 - peak) ** (1.0 / steps)
    for i in range(steps):
        c.setFillAlpha(step_alpha)
        c.circle(cx, cy, r * (1 - i / steps), fill=1, stroke=0)
    c.restoreState()


def _tracked_width(text, font, size, tracking_em=0.0):
    return stringWidth(text, font, size) + size * tracking_em * max(len(text) - 1, 0)


def _draw_tracked(c, text, x, base_y, font, size, color, tracking_em=0.0):
    """Draw left-aligned text with optional CSS-like letter-spacing (em)."""
    to = c.beginText(x, base_y)
    to.setFont(font, size)
    if tracking_em:
        to.setCharSpace(size * tracking_em)
    to.setFillColorRGB(*color)
    to.textOut(text)
    c.drawText(to)


def _load_square_thumb(path, target=512):
    """Load a profile photo as a centre-cropped RGB square, downscaled to
    `target` px. Using JPEG ``draft`` mode makes libjpeg decode at a reduced
    scale, which is dramatically faster (and smaller) than embedding the
    full-resolution original — a single large phone photo used to produce a
    ~40 MB badge PDF and take ~17 s to render."""
    im = Image.open(path)
    try:
        im.draft("RGB", (target, target))
    except Exception:
        pass
    im = ImageOps.exif_transpose(im)
    if im.mode != "RGB":
        im = im.convert("RGB")
    w, h = im.size
    s = min(w, h)
    left = (w - s) // 2
    top = (h - s) // 2
    im = im.crop((left, top, left + s, top + s))
    if s > target:
        resample = getattr(Image, "Resampling", Image).LANCZOS
        im = im.resize((target, target), resample)
    return im


def _draw_round_photo(c, cx, cy, size, path, border=None, border_w=2):
    """Draw a circular profile photo centred at (cx, cy) with diameter `size`
    points, clipped to a circle with a brand-pink border. The image is
    centre-cropped to a square first (like the preview's object-cover) so it
    fills the circle. Returns False when the file can't be loaded."""
    if not path or not os.path.exists(path):
        return False
    try:
        im = _load_square_thumb(path)
    except Exception:
        return False
    r = size / 2.0
    c.saveState()
    clip = c.beginPath()
    clip.circle(cx, cy, r)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(ImageReader(im), cx - r, cy - r, size, size, preserveAspectRatio=False, mask="auto")
    c.restoreState()
    c.saveState()
    c.setStrokeColorRGB(*(border or (254 / 255.0, 80 / 255.0, 103 / 255.0)))
    c.setLineWidth(border_w)
    c.circle(cx, cy, r - border_w / 2.0, fill=0, stroke=1)
    c.restoreState()
    return True


def _render_badge_page(c, p, logo_left, logo_right, primary_rgb, secondary_rgb):
    """Draw a single A5 badge page onto ReportLab canvas c.

    Mirrors the frontend badge preview (BadgeCard.vue, used by BadgeModal /
    My Badge on both the admin and participant sides). BadgeCard is designed at
    a 380px card width that represents the A5 page width, so every measurement
    below is written in those preview pixels and scaled through ``U()`` — that
    keeps the printed page's spacing, type scale and vertical rhythm flowing the
    same way as the on-screen card instead of drifting from it.
    """
    W, H = A5
    PX = W / 380.0  # points per preview pixel

    def U(px):
        return px * PX

    def Y(top):
        return H - top

    def line_base(top, lh_px, fs_px):
        # baseline that vertically centres a font's cap-height in a line box
        return Y(top + U((lh_px + fs_px * 0.72) / 2))

    def wrap(text, font, size, max_w):
        lines, cur = [], ""
        for word in str(text).split():
            trial = f"{cur} {word}".strip()
            if not cur or stringWidth(trial, font, size) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines or [""]

    GRAY_900 = (17 / 255.0, 24 / 255.0, 39 / 255.0)
    GRAY_800 = (31 / 255.0, 41 / 255.0, 55 / 255.0)
    GRAY_600 = (75 / 255.0, 85 / 255.0, 99 / 255.0)
    GRAY_500 = (107 / 255.0, 114 / 255.0, 128 / 255.0)
    ROSE_800 = (159 / 255.0, 18 / 255.0, 57 / 255.0)
    RED = (220 / 255.0, 50 / 255.0, 75 / 255.0)        # rgb(220,50,75)
    PINK = (254 / 255.0, 80 / 255.0, 103 / 255.0)      # rgb(254,80,103)
    FOOTER_END = (214 / 255.0, 44 / 255.0, 68 / 255.0)

    def tint(color, alpha, bg=(1.0, 1.0, 1.0)):
        return tuple(alpha * color[i] + (1 - alpha) * bg[i] for i in range(3))

    # ── White page + decorative blurred blobs (behind everything) ───────────
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, W, H, fill=True, stroke=False)
    _draw_blob(c, U(356), H - U(24), U(72), PINK, peak=0.16)           # top-right
    _draw_blob(c, U(16), H - (H / 3 + U(64)), U(64), PINK, peak=0.12)  # mid-left

    # ── Footer: brand gradient + motif, dates + website, then location ──────
    location = (p.get("location") or "").strip()
    row1_h_px = 14 + 6 + 1 + 6          # content, pb-1.5, border, mb-1.5
    footer_h = U(12 + row1_h_px + (12 if location else 0) + 12)

    _gradient_rect(c, 0, 0, W, footer_h, [
        (0.0, RED), (0.5, PINK), (1.0, FOOTER_END),
    ])
    _draw_diamond_pattern(c, 0, 0, W, footer_h, (1, 1, 1), tile=U(28), alpha=0.15)

    c.saveState()
    c.setStrokeColorRGB(*PINK)
    c.setStrokeAlpha(0.3)
    c.setLineWidth(U(1))
    c.line(0, footer_h - U(0.5), W, footer_h - U(0.5))
    c.restoreState()

    row1_top = footer_h - U(12)
    row1_lh = U(14)
    row1_base = row1_top - (row1_lh + U(10) * 0.72) / 2
    icon_s = U(14)
    _draw_calendar_icon(c, U(16), row1_base - icon_s * 0.18, icon_s, (1, 1, 1))
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", U(10))
    c.drawString(U(16) + icon_s + U(4), row1_base,
                 _format_badge_date_range(p.get("event_start_date"), p.get("event_end_date")) or "")
    c.setFont("Helvetica-Bold", U(9))
    c.drawRightString(W - U(16), row1_base, "WWW.ECSACONM.ORG")

    rule_y = row1_top - row1_lh - U(6)
    c.saveState()
    c.setStrokeColorRGB(1, 1, 1)
    c.setStrokeAlpha(0.25)
    c.setLineWidth(U(1))
    c.line(U(16), rule_y, W - U(16), rule_y)
    c.restoreState()

    if location:
        row2_top = rule_y - U(1) - U(6)
        row2_base = row2_top - (U(12) + U(10) * 0.72) / 2
        loc_size = U(10)
        loc_w = stringWidth(location, "Helvetica-Bold", loc_size)
        pin_s = U(12)
        block_w = pin_s + U(4) + loc_w
        lx = W / 2 - block_w / 2
        _draw_pin_icon(c, lx + pin_s / 2, row2_base + loc_size * 0.72, pin_s, (1, 1, 1))
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", loc_size)
        c.drawString(lx + pin_s + U(4), row2_base, location)

    # ── Header: logos flanking the title, fading divider ────────────────────
    # (The on-screen preview draws a punch-hole graphic here — see BadgeCard.vue's
    # "Punch hole slot" — but on a printed/laminated badge that reads as a stray
    # black dot rather than a real hole, so the PDF skips drawing it and only
    # keeps its vertical spacing.)
    top = U(10)
    hole_h = U(12)
    top += hole_h + U(8)

    title = _parse_badge_title(p.get("event_name") or "")
    title_h = 20                              # ordinal + org line (leading-none)
    if title["subtitle"]:
        title_h += 4 + 12                     # mt-1 + subtitle line
    if title["pill"]:
        title_h += 6 + 15                     # mt-1.5 + pill (py + text + border)

    logo_d = U(64)
    row_h = max(logo_d, U(title_h))
    row_top = top
    logo_cy = Y(row_top + row_h / 2)
    left_cx = U(16) + logo_d / 2
    right_cx = W - U(16) - logo_d / 2

    # ECSA (left): white circle with a pink border, logo inset like `p-1`
    c.saveState()
    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(*PINK)
    c.setLineWidth(U(2))
    c.circle(left_cx, logo_cy, logo_d / 2 - U(1), fill=1, stroke=1)
    c.restoreState()
    left_img = U(52)
    c.drawImage(logo_left, left_cx - left_img / 2, logo_cy - left_img / 2, left_img, left_img,
                preserveAspectRatio=True, mask="auto")

    # ECSACONM (right): solid brand-red circle, no border
    c.saveState()
    c.setFillColorRGB(*RED)
    c.circle(right_cx, logo_cy, logo_d / 2, fill=1, stroke=0)
    c.restoreState()
    right_img = U(56)
    c.drawImage(logo_right, right_cx - right_img / 2, logo_cy - right_img / 2, right_img, right_img,
                preserveAspectRatio=True, mask="auto")

    # Title block, vertically centred in the logo row and centred between logos
    title_x0 = left_cx + logo_d / 2 + U(8)
    title_x1 = right_cx - logo_d / 2 - U(8)
    title_cx = (title_x0 + title_x1) / 2
    ty = row_top + (row_h - U(title_h)) / 2

    ord_size, org_size = U(18), U(20)
    ord_text = f"{title['ordinal']} " if title["ordinal"] else ""
    ord_w = stringWidth(ord_text, "Helvetica-Bold", ord_size)
    org_w = stringWidth(title["org"], "Helvetica-Bold", org_size)
    tx = title_cx - (ord_w + org_w) / 2
    if ord_text:
        c.setFillColorRGB(*GRAY_800)
        c.setFont("Helvetica-Bold", ord_size)
        c.drawString(tx, line_base(ty, 20, 20), ord_text)
    c.setFillColorRGB(*RED)
    c.setFont("Helvetica-Bold", org_size)
    c.drawString(tx + ord_w, line_base(ty, 20, 20), title["org"])
    ty += U(20)

    if title["subtitle"]:
        ty += U(4)
        c.setFillColorRGB(*GRAY_600)
        c.setFont("Helvetica-Bold", U(10))
        for line in wrap(title["subtitle"].upper(), "Helvetica-Bold", U(10), title_x1 - title_x0)[:2]:
            c.drawCentredString(title_cx, line_base(ty, 12, 10), line)
            ty += U(12)

    if title["pill"]:
        ty += U(6)
        pill_text = title["pill"]
        pill_size = U(9)
        pill_w = stringWidth(pill_text, "Helvetica-Bold", pill_size) + U(20)
        pill_h = U(15)
        pill_y = Y(ty + U(15))
        c.setFillColorRGB(*tint(PINK, 0.08))
        c.setStrokeColorRGB(*tint(PINK, 0.25))
        c.setLineWidth(U(1))
        c.roundRect(title_cx - pill_w / 2, pill_y, pill_w, pill_h, pill_h / 2, fill=1, stroke=1)
        c.setFillColorRGB(*RED)
        c.setFont("Helvetica-Bold", pill_size)
        c.drawCentredString(title_cx, pill_y + pill_h / 2 - pill_size * 0.36, pill_text)

    top = row_top + row_h

    # Divider — fades to transparent at both ends (linear-gradient over white)
    top += U(8)
    _gradient_rect(c, 0, Y(top + U(2)), W, U(2), [
        (0.0, (1, 1, 1)), (0.5, tint(PINK, 0.4)), (1.0, (1, 1, 1)),
    ])
    top += U(2) + U(4) + U(4) + U(2)   # divider, header pb-1, section pt-1, name mt-1

    # ── Name ────────────────────────────────────────────────────────────────
    full_name = re.sub(
        r"\s+", " ",
        f"{p.get('title', '')} {p.get('firstname', '')} {p.get('middle_name', '')} {p.get('lastname', '')}".strip(),
    )
    c.setFillColorRGB(*GRAY_900)
    c.setFont("Helvetica-Bold", U(22))
    for line in (wrap(full_name, "Helvetica-Bold", U(22), W - U(40))[:2] or ["—"]):
        c.drawCentredString(W / 2, line_base(top, 27, 22), line)
        top += U(27)

    # Round profile photo between the name and the category bar (if uploaded)
    photo = p.get("photo")
    if photo and os.path.exists(photo):
        top += U(4)
        photo_size = U(80)
        if _draw_round_photo(c, W / 2, Y(top + photo_size / 2), photo_size, photo):
            top += photo_size + U(8)

    top += U(8)   # category bar mt-2

    # ── Category bar (role-coloured gradient, white tracked caps) ───────────
    bar_x, bar_w = U(20), W - U(40)
    bar_h, bar_r = U(32), U(8)
    bar_bottom = Y(top + U(32))
    role_key = (p.get("participation_role") or "delegate").strip().lower()
    bar_dark, bar_light, bar_edge = badge_category_gradient(role_key)
    bar_dark_rgb, bar_light_rgb, bar_edge_rgb = hex_to_rgb(bar_dark), hex_to_rgb(bar_light), hex_to_rgb(bar_edge)
    c.saveState()
    bar_clip = c.beginPath()
    bar_clip.roundRect(bar_x, bar_bottom, bar_w, bar_h, bar_r)
    c.clipPath(bar_clip, stroke=0, fill=0)
    _gradient_rect(c, bar_x, bar_bottom, bar_w, bar_h, [
        (0.0, bar_dark_rgb), (0.5, bar_light_rgb), (1.0, bar_dark_rgb),
    ])
    c.restoreState()
    c.saveState()
    c.setStrokeColorRGB(*bar_edge_rgb)
    c.setStrokeAlpha(0.4)
    c.setLineWidth(U(1))
    c.roundRect(bar_x, bar_bottom, bar_w, bar_h, bar_r, fill=0, stroke=1)
    c.restoreState()
    bar_size = U(19)
    bar_text = (p.get("participation_role") or "Delegate").upper()
    _draw_tracked(c, bar_text, W / 2 - _tracked_width(bar_text, "Helvetica-Bold", bar_size, 0.14) / 2,
                  bar_bottom + bar_h / 2 - bar_size * 0.36, "Helvetica-Bold", bar_size, (1, 1, 1), 0.14)
    top += U(32) + U(12)   # bar + info mt-3

    # ── Designation pill ────────────────────────────────────────────────────
    designation = (p.get("designation") or "").strip()
    if designation:
        d_text = designation.upper()
        d_size = U(12)
        d_h = U(21)
        d_w = stringWidth(d_text, "Helvetica-Bold", d_size) + U(24)
        d_bottom = Y(top + U(21))
        c.setFillColorRGB(*tint(PINK, 0.06))
        c.setStrokeColorRGB(*tint(PINK, 0.3))
        c.setLineWidth(U(1))
        c.roundRect(W / 2 - d_w / 2, d_bottom, d_w, d_h, d_h / 2, fill=1, stroke=1)
        _draw_tracked(c, d_text, W / 2 - _tracked_width(d_text, "Helvetica-Bold", d_size, 0.025) / 2,
                      d_bottom + d_h / 2 - d_size * 0.36, "Helvetica-Bold", d_size, ROSE_800, 0.025)
        top += d_h + U(4)

    # ── Institution & country ───────────────────────────────────────────────
    organisation = (p.get("organisation") or "").strip()
    if organisation:
        top += U(2)   # institution pt-0.5
        c.setFillColorRGB(*GRAY_800)
        c.setFont("Helvetica-Bold", U(14))
        for line in wrap(organisation, "Helvetica-Bold", U(14), W - U(40))[:2]:
            c.drawCentredString(W / 2, line_base(top, 18, 14), line)
            top += U(18)
    country = (p.get("country") or "").strip()
    if country:
        top += U(4)
        c_size = U(12)
        c_w = stringWidth(country, "Helvetica-Bold", c_size)
        pin_s = U(14)
        block_w = pin_s + U(4) + c_w
        base_c = line_base(top, 15, 12)
        _draw_pin_icon(c, W / 2 - block_w / 2 + pin_s / 2, base_c + c_size * 0.72, pin_s, PINK)
        c.setFillColorRGB(*GRAY_500)
        c.setFont("Helvetica-Bold", c_size)
        c.drawString(W / 2 - block_w / 2 + pin_s + U(4), base_c, country)
        top += U(15)

    # ── QR code card (bordered, ID printed inside below the code) ───────────
    top += U(6)   # section py-2
    theme = (p.get("event_theme") or "").strip()
    theme_lines = wrap(f'Theme: "{theme}"', "Helvetica-Oblique", U(11), W - U(40))[:2] if theme else []
    theme_block = (U(6) + len(theme_lines) * U(13)) if theme_lines else 0

    card_pad = U(4)
    available = (H - footer_h) - top - U(6) - theme_block
    qr_size = max(U(36), min(U(120), available - card_pad * 2))
    card_w = qr_size + card_pad * 2
    card_h = qr_size + card_pad * 2
    card_x = (W - card_w) / 2
    card_bottom = H - top - card_h

    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(*tint(PINK, 0.25))
    c.setLineWidth(U(1))
    c.roundRect(card_x, card_bottom, card_w, card_h, U(12), fill=1, stroke=1)

    qr_data = f"{CLIENT_ORIGIN}/#/user-event-status/{p['registration_id']}/{p['event_id']}/"
    qr = qrcode.make(qr_data)
    qr_buf = BytesIO()
    qr.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    c.drawImage(ImageReader(qr_buf), card_x + card_pad, card_bottom + card_pad, qr_size, qr_size)

    top += card_h

    # ── Theme ───────────────────────────────────────────────────────────────
    if theme_lines:
        top += U(6)   # theme mt-2
        th_size = U(11)
        for i, line in enumerate(theme_lines):
            base = line_base(top, 14, 11)
            if i == 0 and line.startswith("Theme:"):
                label, rest = "Theme:", line[len("Theme:"):]
                label_size = U(10)
                label_w = _tracked_width(label, "Helvetica-Bold", label_size, 0.025)
                rest_w = stringWidth(rest, "Helvetica-Oblique", th_size)
                lx = W / 2 - (label_w + rest_w) / 2
                _draw_tracked(c, label, lx, base, "Helvetica-Bold", label_size, RED, 0.025)
                c.setFillColorRGB(*GRAY_500)
                c.setFont("Helvetica-Oblique", th_size)
                c.drawString(lx + label_w, base, rest)
            else:
                c.setFillColorRGB(*GRAY_500)
                c.setFont("Helvetica-Oblique", th_size)
                c.drawCentredString(W / 2, base, line)
            top += U(13)
    top += U(6)   # section py-2 bottom


def _draw_badges_two_up(c, participants, logo_left, logo_right, primary_rgb, secondary_rgb):
    """Lay out 2 badges per landscape A4 sheet, each scaled from its A5 design
    down to ~118x168mm — sized to the actual badge-holder pocket in use.

    Both A6 (~105x148mm, 4-up) and full A5 (148x210mm, 2-up) were tried and
    measured against the holder: A6 left visible slack (top ~10mm, side ~8mm
    around the card — pocket is roughly 121x168mm), and A5 was clearly larger
    than the pocket. This targets the pocket estimate directly instead."""
    a4_w, a4_h = landscape(A4)
    a5_w, a5_h = A5
    target_w, target_h = 120 * mm, 168 * mm
    scale = min(target_w / a5_w, target_h / a5_h)
    bw, bh = a5_w * scale, a5_h * scale

    cell_w = a4_w / 2
    margin_y = (a4_h - bh) / 2

    for index, p in enumerate(participants):
        slot = index % 2
        if slot == 0 and index:
            c.showPage()
        x = cell_w * slot + (cell_w - bw) / 2
        y = margin_y

        c.saveState()
        c.translate(x, y)
        c.scale(scale, scale)
        _render_badge_page(c, p, logo_left, logo_right, primary_rgb, secondary_rgb)
        c.restoreState()

        # faint cut guide around the badge
        c.saveState()
        c.setStrokeColorRGB(0.85, 0.85, 0.85)
        c.setLineWidth(0.4)
        c.rect(x, y, bw, bh, fill=0, stroke=1)
        c.restoreState()

    c.showPage()


@router.get("/{event_id}/participants/badges")
async def download_participant_badges_pdf(
    request: Request,
    event_id: int,
    current_user: user_dependency,
    paid: Literal["all", "true", "false"] = Query("all"),
    ids: str = Query(""),
    db: Session = Depends(get_db),
    dependency=Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("VIEW_EVENT", current_user["user_id"])
    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user["user_id"],
        "DOWNLOAD_BADGES",
        current_user["username"],
        client_ip,
        f"Downloaded participant badges for event {event_id} with filter paid={paid}",
    )

    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    primary_color = (event.org_unit.primary_color or "#0095B6") if event.org_unit else "#0095B6"
    secondary_color = (event.org_unit.secondary_color or "#F7941D") if event.org_unit else "#F7941D"
    primary_rgb = hex_to_rgb(primary_color)
    secondary_rgb = hex_to_rgb(secondary_color)

    id_filter = (
        {int(x) for x in ids.split(",") if x.strip().isdigit()} if ids else None
    )

    rows = []
    for reg in event.registrations:
        if reg.deleted_at is not None:
            continue
        if id_filter is not None and reg.id not in id_filter:
            continue
        user = reg.user
        profile = user.user_profile[0] if user.user_profile else None
        country = profile.country.country if profile and profile.country else None
        organisation = profile.organisation if profile else None
        role_key = (
            reg.participation_role.name
            if hasattr(reg.participation_role, "name")
            else str(reg.participation_role).lower()
        )
        rows.append(
            (
                reg,
                {
                    "registration_id": reg.id,
                    "event_id": event_id,
                    "title": profile.title if profile else "",
                    "firstname": user.firstname,
                    "middle_name": profile.middle_name if profile else "",
                    "lastname": user.lastname,
                    "position": profile.position if profile else "",
                    "designation": profile.designation if profile else "",
                    "organisation": organisation,
                    "country": country,
                    "participation_role": format_badge_category(role_key),
                    "event_name": event.event,
                    "event_theme": event.theme,
                    "location": event.location or "",
                    "event_start_date": event.start_date,
                    "event_end_date": event.end_date,
                    "paid": reg.is_paid,
                    "photo": user.user_photo[0].path if user and user.user_photo and len(user.user_photo) > 0 else None,
                },
            )
        )

    if paid != "all":
        is_paid = paid == "true"
        rows = [(r, p) for r, p in rows if p["paid"] == is_paid]

    if not rows:
        raise HTTPException(status_code=404, detail="No participants found")

    participants = [p for _, p in rows]
    exported_regs = [r for r, _ in rows]

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    logo_left = convert_png_to_rgb("assets/logo_left.png")
    logo_right = convert_png_to_rgb("assets/logo.png")

    _draw_badges_two_up(c, participants, logo_left, logo_right, primary_rgb, secondary_rgb)

    exported_at = datetime.utcnow()
    for reg in exported_regs:
        reg.badge_exported_at = exported_at
    db.commit()

    c.save()
    buffer.seek(0)

    safe_event_name = sanitize_filename(event.event)
    ascii_filename = f"{safe_event_name}_participant_badges.pdf"
    utf8_filename = urllib.parse.quote(ascii_filename)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={ascii_filename}; filename*=UTF-8''{utf8_filename}"
        },
    )


@router.get("/{event_id}/participants/{registration_id}/badge")
async def download_participant_badge_pdf(
    request: Request,
    event_id: int,
    registration_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency=Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("VIEW_EVENT", current_user["user_id"])
    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user["user_id"],
        "DOWNLOAD_BADGE",
        current_user["username"],
        client_ip,
        f"Downloaded badge for registration {registration_id} (event {event_id})",
    )

    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    reg = (
        db.query(Registration)
        .filter(
            Registration.id == registration_id,
            Registration.event_id == event_id,
            Registration.deleted_at == None,
        )
        .first()
    )
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    user = reg.user
    profile = user.user_profile[0] if user.user_profile else None
    country = profile.country.country if profile and profile.country else None
    organisation = profile.organisation if profile else None
    role_key = (
        reg.participation_role.name
        if hasattr(reg.participation_role, "name")
        else str(reg.participation_role).lower()
    )

    primary_color = (event.org_unit.primary_color or "#0095B6") if event.org_unit else "#0095B6"
    secondary_color = (event.org_unit.secondary_color or "#F7941D") if event.org_unit else "#F7941D"
    primary_rgb = hex_to_rgb(primary_color)
    secondary_rgb = hex_to_rgb(secondary_color)

    p = {
        "registration_id": reg.id,
        "event_id": event_id,
        "title": profile.title if profile else "",
        "firstname": user.firstname,
        "middle_name": profile.middle_name if profile else "",
        "lastname": user.lastname,
        "position": profile.position if profile else "",
        "designation": profile.designation if profile else "",
        "organisation": organisation,
        "country": country,
        "participation_role": format_badge_category(role_key),
        "event_name": event.event,
        "event_theme": event.theme,
        "location": event.location or "",
        "event_start_date": event.start_date,
        "event_end_date": event.end_date,
        "paid": reg.is_paid,
        "photo": user.user_photo[0].path if user and user.user_photo and len(user.user_photo) > 0 else None,
    }

    buffer = BytesIO()
    width, height = A5
    c = canvas.Canvas(buffer, pagesize=A5)

    logo_left = convert_png_to_rgb("assets/logo_left.png")
    logo_right = convert_png_to_rgb("assets/logo.png")

    _render_badge_page(c, p, logo_left, logo_right, primary_rgb, secondary_rgb)
    c.showPage()

    reg.badge_exported_at = datetime.utcnow()
    db.commit()

    c.save()
    buffer.seek(0)

    safe_name = sanitize_filename(f"{user.firstname}_{user.lastname}")
    ascii_filename = f"badge_{safe_name}.pdf"
    utf8_filename = urllib.parse.quote(ascii_filename)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={ascii_filename}; filename*=UTF-8''{utf8_filename}"
        },
    )


@router.delete("/{event_id}/badge-exports")
async def clear_badge_exports(
    request: Request,
    event_id: int,
    current_user: user_dependency,
    ids: str = Query(""),
    db: Session = Depends(get_db),
    dependency=Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    """Reset badge_exported_at for registrations of the event, so badges can be
    re-generated/exported. Pass ``ids`` (comma-separated registration ids) to
    clear only a selection; omit it to clear every exported badge.
    ADMIN_DASHBOARD bypasses the check."""
    auth_dependency.secure_access("PRINT_BADGE", current_user["user_id"])
    client_ip = dependency.request_ip(request)

    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    id_filter = (
        {int(x) for x in ids.split(",") if x.strip().isdigit()} if ids else None
    )

    query = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.deleted_at == None,
        Registration.badge_exported_at.isnot(None),
    )
    if id_filter is not None:
        query = query.filter(Registration.id.in_(id_filter))

    cleared = query.update({Registration.badge_exported_at: None})
    db.commit()

    scope = f"selected {len(id_filter)}" if id_filter is not None else "all"
    dependency.log_activity(
        current_user["user_id"],
        "CLEAR_BADGE_EXPORTS",
        current_user["username"],
        client_ip,
        f"Cleared badge export status for {cleared} registrations ({scope}) (event {event_id})",
    )

    return {"status": "success", "cleared": cleared}


@router.get("/{event_id}/my-badge")
async def download_my_badge(
    event_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
):
    """Generate a badge PDF for the currently authenticated paid user."""
    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    reg = db.query(Registration).filter(
        Registration.user_id == current_user["user_id"],
        Registration.event_id == event_id,
        Registration.deleted_at == None,
    ).first()

    if not reg:
        raise HTTPException(status_code=404, detail="You are not registered for this event")
    if not reg.is_paid:
        raise HTTPException(status_code=403, detail="Badge is only available after payment is confirmed")

    user = reg.user
    profile = user.user_profile[0] if user.user_profile else None
    country = profile.country.country if profile and profile.country else None
    organisation = profile.organisation if profile else None
    role_key = (
        reg.participation_role.name
        if hasattr(reg.participation_role, "name")
        else str(reg.participation_role).lower()
    )

    primary_color = (event.org_unit.primary_color or "#0095B6") if event.org_unit else "#0095B6"
    secondary_color = (event.org_unit.secondary_color or "#F7941D") if event.org_unit else "#F7941D"
    primary_rgb = hex_to_rgb(primary_color)
    secondary_rgb = hex_to_rgb(secondary_color)

    p = {
        "registration_id": reg.id,
        "event_id": event_id,
        "title": profile.title if profile else "",
        "firstname": user.firstname,
        "middle_name": profile.middle_name if profile else "",
        "lastname": user.lastname,
        "position": profile.position if profile else "",
        "designation": profile.designation if profile else "",
        "organisation": organisation,
        "country": country,
        "participation_role": format_badge_category(role_key),
        "event_name": event.event,
        "event_theme": event.theme,
        "location": event.location or "",
        "event_start_date": event.start_date,
        "event_end_date": event.end_date,
        "paid": reg.is_paid,
        "photo": user.user_photo[0].path if user and user.user_photo and len(user.user_photo) > 0 else None,
    }

    buffer = BytesIO()
    width, height = A5
    c = canvas.Canvas(buffer, pagesize=A5)

    logo_left = convert_png_to_rgb("assets/logo_left.png")
    logo_right = convert_png_to_rgb("assets/logo.png")

    _render_badge_page(c, p, logo_left, logo_right, primary_rgb, secondary_rgb)
    c.showPage()

    reg.badge_exported_at = datetime.utcnow()
    db.commit()

    c.save()
    buffer.seek(0)

    safe_name = sanitize_filename(f"{user.firstname}_{user.lastname}")
    ascii_filename = f"badge_{safe_name}.pdf"
    utf8_filename = urllib.parse.quote(ascii_filename)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={ascii_filename}; filename*=UTF-8''{utf8_filename}"
        },
    )


@router.get("/{event_id}/attendance")
async def get_event_attendance(
    event_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    """Admin: get all attendance records for an event."""
    auth_dependency.secure_access("VIEW_EVENT", current_user["user_id"])

    from models.models import EventAttendance
    records = (
        db.query(EventAttendance)
        .join(Registration, EventAttendance.registration_id == Registration.id)
        .filter(Registration.event_id == event_id)
        .order_by(EventAttendance.attendance_date.desc())
        .all()
    )

    result = []
    for a in records:
        reg = a.registration
        user = reg.user if reg else None
        profile = user.user_profile[0] if user and user.user_profile else None
        result.append({
            "id": a.id,
            "registration_id": a.registration_id,
            "attendance_date": a.attendance_date,
            "firstname": user.firstname if user else "",
            "lastname": user.lastname if user else "",
            "email": user.email if user else "",
            "organisation": profile.organisation if profile else "",
            "country": profile.country.country if profile and profile.country else "",
            "participation_role": reg.participation_role.name if reg else "",
            "paid": reg.is_paid if reg else False,
        })

    return {"total": len(result), "data": result}
