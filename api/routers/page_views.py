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


def get_auth_dep(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


class PageViewIn(BaseModel):
    page: str
    event_id: Optional[int] = None
    visitor_id: Optional[str] = None
    ref: Optional[str] = None
    source: Optional[str] = None


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
    user_id = parse_ref(body.ref) or (current_user or {}).get("user_id")
    if user_id and not db.query(User.id).filter(User.id == user_id).first():
        user_id = None
    source = body.source if body.source in ALLOWED_SOURCES else None
    db.add(PageView(
        page=body.page,
        event_id=body.event_id,
        visitor_id=visitor_id,
        user_id=user_id,
        source=source,
        user_agent=(request.headers.get("user-agent") or "")[:300] or None,
    ))
    db.commit()
    return {"ok": True}


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

    people_rows = (
        q.filter(PageView.user_id.isnot(None))
        .join(User, User.id == PageView.user_id)
        .with_entities(
            User.id, User.firstname, User.lastname, User.email,
            func.count(PageView.id), func.min(PageView.created_at), func.max(PageView.created_at),
        )
        .group_by(User.id, User.firstname, User.lastname, User.email)
        .order_by(func.max(PageView.created_at).desc())
        .all()
    )

    return {
        "page": page,
        "event_id": event_id,
        "tracking_since": first_at,
        "opens": opens,
        "unique_visitors": unique_visitors,
        "from_email": from_email,
        "identified_people": len(people_rows),
        "hourly": [{"hour": h, "opens": n} for h, n in hourly],
        "people": [
            {
                "user_id": uid,
                "name": f"{(fn or '').strip()} {(ln or '').strip()}".strip(),
                "email": email,
                "opens": n,
                "first_opened": first,
                "last_opened": last,
            }
            for uid, fn, ln, email, n, first, last in people_rows
        ],
    }
