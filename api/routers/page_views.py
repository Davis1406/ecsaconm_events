import re
from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user, get_optional_current_user
from models.models import PageView, User
from utils.page_ref import parse_ref

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]

# Only pages listed here are recorded — the endpoint is public, so it must
# not become a free-form write target.
TRACKED_PAGES = {"programme-rooms-public"}
ALLOWED_SOURCES = {"email", "direct"}
_VISITOR_RE = re.compile(r"^[A-Za-z0-9-]{8,64}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


def get_auth_dep(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


class PageViewIn(BaseModel):
    page: str
    event_id: Optional[int] = None
    visitor_id: Optional[str] = None
    ref: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = None


class IdentifyIn(BaseModel):
    page: str
    email: str
    event_id: Optional[int] = None
    visitor_id: Optional[str] = None


def _clean_email(email) -> Optional[str]:
    e = (email or "").strip().lower()[:255]
    return e if _EMAIL_RE.match(e) else None


def _resolve_viewer(db: Session, ref=None, email=None, current_user=None):
    """(user_id, email) for a page view: a signed ref (certificate-email
    link) wins, then a logged-in session, then the typed email — matched to
    an account when one exists, otherwise kept as-is (unverified)."""
    user = None
    uid = parse_ref(ref) or (current_user or {}).get("user_id")
    if uid:
        user = db.query(User).filter(User.id == uid, User.deleted_at == None).first()
    typed = _clean_email(email)
    if not user and typed:
        user = db.query(User).filter(func.lower(User.email) == typed, User.deleted_at == None).first()
    if user:
        return user.id, (user.email or "").strip().lower() or typed
    return None, typed


@router.post("/")
def record_page_view(
    body: PageViewIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """Record one open of a tracked public page. No login required; a valid
    signed `ref` (from the recipient's certificate-email link) or a logged-in
    session attributes the open to a user."""
    if body.page not in TRACKED_PAGES:
        raise HTTPException(status_code=400, detail="Untracked page")
    visitor_id = body.visitor_id if body.visitor_id and _VISITOR_RE.match(body.visitor_id) else None
    user_id, email = _resolve_viewer(db, body.ref, body.email, current_user)
    source = body.source if body.source in ALLOWED_SOURCES else None
    db.add(PageView(
        page=body.page,
        event_id=body.event_id,
        visitor_id=visitor_id,
        user_id=user_id,
        email=email,
        source=source,
        user_agent=(request.headers.get("user-agent") or "")[:300] or None,
    ))
    db.commit()
    return {"ok": True}


@router.post("/identify")
def identify_viewer(body: IdentifyIn, db: Session = Depends(get_db)):
    """The email a visitor typed into the page's access prompt (asked once
    per device before preview/download). Attributes that device's earlier,
    still-anonymous opens to them. Never blocks access: an email that
    matches no account is recorded as given."""
    if body.page not in TRACKED_PAGES:
        raise HTTPException(status_code=400, detail="Untracked page")
    email = _clean_email(body.email)
    if not email:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    user_id, email = _resolve_viewer(db, email=email)
    visitor_id = body.visitor_id if body.visitor_id and _VISITOR_RE.match(body.visitor_id) else None
    if visitor_id:
        (
            db.query(PageView)
            .filter(PageView.page == body.page, PageView.visitor_id == visitor_id,
                    PageView.user_id == None, PageView.email == None)
            .update({PageView.user_id: user_id, PageView.email: email}, synchronize_session=False)
        )
        db.commit()
    return {"ok": True, "registered": user_id is not None}


@router.get("/stats")
def page_view_stats(
    current_user: user_dependency,
    page: str = "programme-rooms-public",
    event_id: Optional[int] = None,
    since: Optional[datetime] = None,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    """Opens, unique visitors (devices), identified people and an hourly
    series for a tracked page. `since` defaults to all recorded history."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])

    q = db.query(PageView).filter(PageView.page == page)
    if event_id:
        q = q.filter(PageView.event_id == event_id)
    if since:
        q = q.filter(PageView.created_at >= since)

    opens = q.count()
    unique_visitors = q.filter(PageView.visitor_id.isnot(None)).with_entities(
        func.count(func.distinct(PageView.visitor_id))).scalar() or 0
    from_email = q.filter(PageView.source == "email").count()
    first_at = q.with_entities(func.min(PageView.created_at)).scalar()

    hour = func.date_format(PageView.created_at, "%Y-%m-%d %H:00")
    hourly = (
        q.with_entities(hour.label("h"), func.count(PageView.id))
        .group_by("h").order_by("h").all()
    )

    # One entry per person: keyed by account when matched, else by the typed
    # email. `registered` says whether it matched an account.
    people = {}
    for uid, email, created in (
        q.filter((PageView.user_id.isnot(None)) | (PageView.email.isnot(None)))
        .with_entities(PageView.user_id, PageView.email, PageView.created_at)
        .all()
    ):
        key = ("u", uid) if uid else ("e", email)
        p = people.setdefault(key, {"user_id": uid, "email": email, "opens": 0,
                                    "first_opened": created, "last_opened": created})
        p["opens"] += 1
        p["first_opened"] = min(p["first_opened"], created)
        p["last_opened"] = max(p["last_opened"], created)
    uids = [k[1] for k in people if k[0] == "u"]
    users = {u.id: u for u in db.query(User).filter(User.id.in_(uids)).all()} if uids else {}
    people_list = []
    for p in people.values():
        u = users.get(p["user_id"])
        people_list.append({
            **p,
            "name": f"{(u.firstname or '').strip()} {(u.lastname or '').strip()}".strip() if u else "",
            "email": (u.email if u else p["email"]) or "",
            "registered": u is not None,
        })
    people_list.sort(key=lambda p: p["last_opened"], reverse=True)

    return {
        "page": page,
        "event_id": event_id,
        "tracking_since": first_at,
        "opens": opens,
        "unique_visitors": unique_visitors,
        "from_email": from_email,
        "identified_people": len(people_list),
        "hourly": [{"hour": h, "opens": n} for h, n in hourly],
        "people": people_list,
    }
