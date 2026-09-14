import os
import re
import io
import uuid
import zipfile
from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user
from models.models import (
    ProgrammeEntry, User, Registration, Event,
    Abstract, AbstractAuthor, AbstractStatus, PresentationType,
)

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]

PROGRAMME_UPLOAD_DIR = "uploads/presentations"
os.makedirs(PROGRAMME_UPLOAD_DIR, exist_ok=True)
ALLOWED_PRESENTATION_EXTS = {".pdf", ".pptx", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
MAX_PRESENTATION_MB = 100
PREVIEW_MEDIA_TYPES = {
    ".pdf": "application/pdf",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
}

DEFAULT_EVENT_ID = 1


def get_auth_dep(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


# ── Name matching (ported from the summary-builder bestMatch) ────────────────
def _norm(s) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w ]", " ", str(s or "").lower())).strip()


def _parts(n) -> list:
    return [p for p in _norm(n).split(" ") if p]


def _surname(n) -> str:
    p = _parts(n)
    return p[-1] if p else ""


def _firstname(n) -> str:
    p = _parts(n)
    if not p:
        return ""
    # Space-joined, not concatenated — a concatenated "getrude m sibuchi" ->
    # "getrudemsibuchi" can never equal or share tokens with a candidate's
    # first name, so 3+-word given names (common in this dataset) always
    # scored as a bare surname-only match. Space-joining lets both the exact
    # match and the per-word overlap bonus below actually fire.
    return " ".join(p[:-1])


def _name_score(pname, cand_first, cand_last):
    """Fuzzy surname+firstname score between a free-typed name (pname, e.g.
    from the programme book) and a candidate (first, last) on record.
    Returns None if the surname doesn't plausibly match at all."""
    sn, fn = _surname(pname), _firstname(pname)
    rsn = _norm(cand_last or "")
    rfn = _norm(cand_first or "")
    if not rsn:
        return None
    if not (rsn == sn or (len(rsn) >= 5 and rsn[:4] == sn[:4])):
        return None
    sc = 2
    if fn and rfn:
        if _norm(fn) == rfn:
            sc += 4
        elif fn[0] == rfn[0]:
            sc += 1
        else:
            sc -= 1
        for w in fn.split(" "):
            if w and w in rfn.split(" "):
                sc += 2
    return sc


def best_registration_match(pname, reg_rows):
    """reg_rows: list of dicts {user_id, first, last, is_paid}. Mirrors the JS bestMatch."""
    best, best_score = None, -1
    for r in reg_rows:
        sc = _name_score(pname, r["first"], r["last"])
        if sc is not None and sc > best_score:
            best_score = sc
            best = r
    if not best or best_score < 3:
        return None
    return {"id": best["user_id"], "first": best["first"], "last": best["last"],
            "paid": best["is_paid"], "score": best_score}


# ── Matching programme slots to submitted Abstracts ──────────────────────────
# The programme book's presenter_name/title are typed by hand from the
# official schedule and often drift from what was actually submitted (typos,
# reworded titles, middle names dropped, etc.) — so we match by presenter
# name only, not title, and let the title differ.
def _presentation_types_for(category):
    if category == "oral":
        return [PresentationType.oral, PresentationType.either]
    if category == "poster":
        return [PresentationType.poster, PresentationType.either]
    return [PresentationType.oral, PresentationType.poster, PresentationType.either]


def _load_abstract_candidates(db: Session, event_id: int, category: str):
    """One row per accepted abstract of the given category: its presenting
    author (falling back to the first-listed author if none is flagged)."""
    rows = (
        db.query(Abstract.id, Abstract.title, Abstract.presentation_file,
                  AbstractAuthor.firstname, AbstractAuthor.lastname,
                  AbstractAuthor.is_presenting, AbstractAuthor.author_order)
        .join(AbstractAuthor, AbstractAuthor.abstract_id == Abstract.id)
        .filter(
            Abstract.event_id == event_id,
            Abstract.deleted_at == None,
            Abstract.status == AbstractStatus.accepted,
            Abstract.presentation_type.in_(_presentation_types_for(category)),
        )
        .all()
    )
    by_abstract = {}
    for r in rows:
        by_abstract.setdefault(r.id, []).append(r)
    out = []
    for abstract_id, authors in by_abstract.items():
        presenting = [a for a in authors if a.is_presenting]
        chosen = presenting[0] if presenting else min(authors, key=lambda a: a.author_order)
        out.append({
            "abstract_id": abstract_id,
            "title": authors[0].title,
            "has_presentation": bool(authors[0].presentation_file),
            "presentation_ext": os.path.splitext(authors[0].presentation_file)[-1].lower() if authors[0].presentation_file else None,
            "first": chosen.firstname,
            "last": chosen.lastname,
        })
    return out


def _compute_abstract_matches(db: Session, event_id: int, category: str):
    """Greedy one-to-one best-score pairing of programme entries to abstracts
    by presenter name. Returns matches plus what's left unmatched on both
    sides, for manual follow-up."""
    entries = (
        db.query(ProgrammeEntry)
        .filter(
            ProgrammeEntry.event_id == event_id,
            ProgrammeEntry.deleted_at == None,
            ProgrammeEntry.category == category,
        )
        .order_by(ProgrammeEntry.sort_order.asc())
        .all()
    )
    candidates = _load_abstract_candidates(db, event_id, category)

    pairs = []
    for e in entries:
        if not e.presenter_name:
            continue
        for c in candidates:
            score = _name_score(e.presenter_name, c["first"], c["last"])
            if score is not None and score >= 3:
                pairs.append((score, e, c))
    pairs.sort(key=lambda p: -p[0])

    used_entries, used_abstracts = set(), set()
    matches = []
    for score, e, c in pairs:
        if e.id in used_entries or c["abstract_id"] in used_abstracts:
            continue
        used_entries.add(e.id)
        used_abstracts.add(c["abstract_id"])
        corrected = " ".join(p for p in [(c["first"] or "").strip(), (c["last"] or "").strip()] if p)
        matches.append({
            "entry_id": e.id,
            "code": e.code,
            "day": e.day,
            "room": e.room,
            "session": e.session,
            "current_presenter_name": e.presenter_name,
            "current_title": e.title,
            "corrected_name": corrected,
            "name_changed": _norm(corrected) != _norm(e.presenter_name or ""),
            "abstract_id": c["abstract_id"],
            "abstract_title": c["title"],
            "abstract_has_presentation": c["has_presentation"],
            "abstract_presentation_ext": c["presentation_ext"],
            "score": score,
            "already_linked": e.abstract_id == c["abstract_id"],
        })
    matches.sort(key=lambda m: -m["score"])

    matched_entry_ids = {m["entry_id"] for m in matches}
    matched_abstract_ids = {m["abstract_id"] for m in matches}
    unmatched_entries = [
        {"entry_id": e.id, "code": e.code, "day": e.day, "room": e.room,
         "presenter_name": e.presenter_name, "title": e.title}
        for e in entries if e.id not in matched_entry_ids
    ]
    unmatched_abstracts = [
        {"abstract_id": c["abstract_id"], "title": c["title"],
         "has_presentation": c["has_presentation"],
         "presenter": " ".join(p for p in [(c["first"] or "").strip(), (c["last"] or "").strip()] if p)}
        for c in candidates if c["abstract_id"] not in matched_abstract_ids
    ]
    return {
        "matches": matches,
        "unmatched_entries": unmatched_entries,
        "unmatched_abstracts": unmatched_abstracts,
        "total_entries": len(entries),
        "total_abstracts": len(candidates),
    }


def _load_reg_rows(db: Session, event_id: int):
    rows = (
        db.query(User.id, User.firstname, User.lastname, Registration.id.label("reg_id"), Registration.paid)
        .join(Registration, Registration.user_id == User.id)
        .filter(Registration.event_id == event_id, Registration.deleted_at == None)
        .all()
    )
    out = []
    for r in rows:
        out.append({
            "user_id": r.id,
            "first": r.firstname or "",
            "last": r.lastname or "",
            "is_paid": bool(r.paid),
        })
    return out


def _effective_presentation_file(entry: ProgrammeEntry):
    """The slide file to serve for this entry: the one uploaded directly
    against it (via the Rooms admin page) if there is one, else the file the
    presenter uploaded when submitting the abstract it's linked to. Lets
    preview/download/zip work for a slot the whole moment it's matched to an
    abstract, even before anyone re-uploads anything here."""
    if entry.presentation_file:
        return entry.presentation_file
    abstract = getattr(entry, "abstract", None)
    if abstract and abstract.presentation_file:
        return abstract.presentation_file
    return None


def _serialize_base(entry: ProgrammeEntry):
    """Fields safe to hand to anyone with the link (public room-view page) —
    no registration/payment status, no raw server file paths."""
    eff = _effective_presentation_file(entry)
    return {
        "id": entry.id,
        "event_id": entry.event_id,
        "category": entry.category,
        "day": entry.day,
        "session": entry.session,
        "room": entry.room,
        "code": entry.code,
        "theme": entry.theme,
        "title": entry.title,
        "presenter_name": entry.presenter_name,
        "role": entry.role,
        "activity": entry.activity,
        "original_presenter": entry.original_presenter,
        "is_substitution": bool(entry.is_substitution),
        "notes": entry.notes,
        "sort_order": entry.sort_order,
        "abstract_id": entry.abstract_id,
        # whether *something* can be previewed/downloaded for this slot, and
        # its extension — never the raw on-disk path. Same URL either way:
        # GET /programme/{id}/preview-presentation|download-presentation.
        "has_presentation": bool(eff),
        "presentation_ext": os.path.splitext(eff)[-1].lower() if eff else None,
        "presentation_source": "entry" if entry.presentation_file else ("abstract" if eff else None),
    }


def _serialize(entry: ProgrammeEntry, match=None):
    """Admin view: base fields plus the entry's own upload path/timestamp and
    live registration/payment match status."""
    base = _serialize_base(entry)
    base.update({
        "presentation_file": entry.presentation_file,
        "presentation_uploaded_at": entry.presentation_uploaded_at.isoformat() if entry.presentation_uploaded_at else None,
        # live registration / payment status
        "status": "registered_paid" if match and match["paid"] else (
            "registered_unpaid" if match else "not_registered"),
        "registered": bool(match),
        "paid": bool(match and match["paid"]),
        "match_score": match["score"] if match else None,
        "matched_user_id": match["id"] if match else None,
        "matched_first": match["first"] if match else None,
        "matched_last": match["last"] if match else None,
    })
    return base


# ── Programme listing ────────────────────────────────────────────────────────
@router.get("")
def list_programme(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(DEFAULT_EVENT_ID),
    category: str = Query(None),       # plenary | oral | poster
    day: str = Query(None),            # Day 1 | Day 2 | Day 3 | Day 1-3
    room: str = Query(None),
    session: str = Query(None),
    search: str = Query(None),
    skip: int = 0,
    limit: int = 500,
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    q = db.query(ProgrammeEntry).options(joinedload(ProgrammeEntry.abstract)).filter(
        ProgrammeEntry.event_id == event_id,
        ProgrammeEntry.deleted_at == None,
    )
    if category:
        q = q.filter(ProgrammeEntry.category == category)
    if day:
        q = q.filter(ProgrammeEntry.day == day)
    if room:
        q = q.filter(ProgrammeEntry.room == room)
    if session:
        q = q.filter(ProgrammeEntry.session == session)
    if search:
        term = f"%{search}%"
        q = q.filter(or_(
            ProgrammeEntry.presenter_name.ilike(term),
            ProgrammeEntry.title.ilike(term),
            ProgrammeEntry.code.ilike(term),
            ProgrammeEntry.role.ilike(term),
        ))
    total = q.count()
    entries = q.order_by(
        ProgrammeEntry.day.asc(),
        ProgrammeEntry.category.asc(),
        ProgrammeEntry.session.asc(),
        ProgrammeEntry.sort_order.asc(),
    ).offset(skip).limit(limit).all()

    reg_rows = _load_reg_rows(db, event_id)
    cache = {}
    result = []
    for e in entries:
        name = e.presenter_name or ""
        key = _norm(name)
        if name and key not in cache:
            cache[key] = best_registration_match(name, reg_rows)
        result.append(_serialize(e, cache.get(key)))
    return {"data": result, "total": total}


# ── Aggregate counts (KPI cards on the summary page) ─────────────────────────
@router.get("/counts")
def programme_counts(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(DEFAULT_EVENT_ID),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    entries = db.query(ProgrammeEntry).filter(
        ProgrammeEntry.event_id == event_id,
        ProgrammeEntry.deleted_at == None,
    ).all()
    reg_rows = _load_reg_rows(db, event_id)
    cache = {}
    by_day = {}
    by_day_category = {}
    totals = {"total": 0, "registered": 0, "paid": 0, "unpaid": 0, "not_registered": 0}
    for e in entries:
        name = e.presenter_name or ""
        key = _norm(name)
        if name and key not in cache:
            cache[key] = best_registration_match(name, reg_rows)
        m = cache.get(key)
        category_key = "paid" if (m and m["paid"]) else ("unpaid" if m else "not_registered")
        day = e.day or "Unassigned"
        cat = e.category or "?"
        totals["total"] += 1
        totals["registered"] += 1 if m else 0
        totals[category_key] += 1
        by_day.setdefault(day, {
            "day": day, "total": 0, "registered": 0, "paid": 0, "unpaid": 0, "not_registered": 0,
        })
        by_day[day]["total"] += 1
        by_day[day]["registered"] += 1 if m else 0
        by_day[day][category_key] += 1
        by_day_category.setdefault(day, {}).setdefault(cat, {
            "category": cat, "total": 0, "registered": 0, "paid": 0, "unpaid": 0, "not_registered": 0,
        })
        dc = by_day_category[day][cat]
        dc["total"] += 1
        dc["registered"] += 1 if m else 0
        dc[category_key] += 1
    return {
        "totals": totals,
        "by_day": list(by_day.values()),
        "by_day_category": {d: list(c.values()) for d, c in by_day_category.items()},
    }


# ── Rooms summary (counts per room/day for the rooms page) ───────────────────
@router.get("/rooms")
def programme_rooms(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(DEFAULT_EVENT_ID),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    entries = db.query(ProgrammeEntry).options(joinedload(ProgrammeEntry.abstract)).filter(
        ProgrammeEntry.event_id == event_id,
        ProgrammeEntry.deleted_at == None,
    ).all()
    reg_rows = _load_reg_rows(db, event_id)
    cache = {}
    rooms = {}   # (day, room) -> {total, with_slide, entries: [...]}
    order = {}
    for e in entries:
        name = e.presenter_name or ""
        key = _norm(name)
        if name and key not in cache:
            cache[key] = best_registration_match(name, reg_rows)
        day = e.day or "Unassigned"
        room_label = e.room or "Unassigned"
        order.setdefault((day, room_label), len(order))
        bucket = rooms.setdefault((day, room_label), {
            "day": day, "room": room_label,
            "total": 0, "with_slide": 0, "entries": [],
        })
        bucket["total"] += 1
        if _effective_presentation_file(e):
            bucket["with_slide"] += 1
        bucket["entries"].append(_serialize(e, cache.get(key)))
    result = []
    for (day, room), bucket in sorted(rooms.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        bucket["entries"].sort(key=lambda x: (x["session"] or "", x["code"] or "", x["title"] or ""))
        result.append({"day": bucket["day"], "room": bucket["room"], "total": bucket["total"],
                        "with_slide": bucket["with_slide"], "entries": bucket["entries"]})
    return {"data": result}


# ── Presenters who have uploaded slides (for room assignment) ─────────────────
def _load_presenter_candidates(db: Session, event_id: int, with_slides_only: bool = True):
    """One row per accepted abstract of this event with its presenting author
    (falling back to the first-listed author): the data the secretariat needs
    to decide who still needs a room. with_slides_only keeps presenters who
    haven't uploaded anything yet out of the assignable list."""
    q = (
        db.query(
            Abstract.id, Abstract.title, Abstract.presentation_file,
            Abstract.presentation_uploaded_at, Abstract.presentation_type,
            AbstractAuthor.firstname, AbstractAuthor.lastname,
            AbstractAuthor.is_presenting, AbstractAuthor.author_order,
        )
        .join(AbstractAuthor, AbstractAuthor.abstract_id == Abstract.id)
        .filter(
            Abstract.event_id == event_id,
            Abstract.deleted_at == None,
            Abstract.status == AbstractStatus.accepted,
        )
    )
    if with_slides_only:
        q = q.filter(Abstract.presentation_file.isnot(None))
    rows = q.all()
    by_abstract = {}
    for r in rows:
        by_abstract.setdefault(r.id, []).append(r)
    out = []
    for abstract_id, authors in by_abstract.items():
        presenting = [a for a in authors if a.is_presenting]
        chosen = presenting[0] if presenting else min(authors, key=lambda a: a.author_order)
        out.append({
            "abstract_id": abstract_id,
            "title": authors[0].title,
            "has_presentation": bool(authors[0].presentation_file),
            "presentation_ext": os.path.splitext(authors[0].presentation_file)[-1].lower() if authors[0].presentation_file else None,
            "presentation_uploaded_at": authors[0].presentation_uploaded_at.isoformat() if authors[0].presentation_uploaded_at else None,
            "presentation_type": authors[0].presentation_type.value if authors[0].presentation_type else None,
            "first": chosen.firstname,
            "last": chosen.lastname,
        })
    return out


@router.get("/presenters-with-slides")
def presenters_with_slides(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(DEFAULT_EVENT_ID),
):
    """Secretariat pick-list: accepted abstracts whose presenter has already
    uploaded slides, with whether they already sit in a programme slot (and
    where). Used to decide who still needs to be assigned to a room/day."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    candidates = _load_presenter_candidates(db, event_id, with_slides_only=True)

    assigned_info = {}
    entries = db.query(ProgrammeEntry).filter(
        ProgrammeEntry.event_id == event_id,
        ProgrammeEntry.deleted_at == None,
        ProgrammeEntry.abstract_id != None,
    ).all()
    for e in entries:
        assigned_info.setdefault(e.abstract_id, []).append({
            "entry_id": e.id, "room": e.room, "day": e.day, "session": e.session,
            "category": e.category, "code": e.code,
        })

    data = []
    for c in candidates:
        info = assigned_info.get(c["abstract_id"], [])
        data.append({
            "abstract_id": c["abstract_id"],
            "title": c["title"],
            "presenter": " ".join(p for p in [(c["first"] or "").strip(), (c["last"] or "").strip()] if p),
            "presentation_ext": c["presentation_ext"],
            "presentation_uploaded_at": c["presentation_uploaded_at"],
            "presentation_type": c["presentation_type"],
            "has_presentation": True,
            "assigned": bool(info),
            "entries": info,
        })
    data.sort(key=lambda d: (d["presenter"] or "").lower())
    return {
        "data": data,
        "total": len(data),
        "assigned": sum(1 for d in data if d["assigned"]),
        "unassigned": sum(1 for d in data if not d["assigned"]),
    }


class AssignPresentersSchema(BaseModel):
    abstract_ids: List[int]
    room: str
    day: Optional[str] = "Day 1"
    session: Optional[str] = None
    category: Optional[str] = None   # oral | poster (defaults from the abstract)


@router.post("/assign-presenters")
def assign_presenters(
    payload: AssignPresentersSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(DEFAULT_EVENT_ID),
):
    """Creates a programme slot for each selected presenter (who already has
    slides) in the given room/day/session. If a slot for that abstract already
    exists, it's moved instead of duplicated."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    if not payload.abstract_ids:
        raise HTTPException(status_code=400, detail="Select at least one presenter.")
    room = (payload.room or "").strip()
    if not room:
        raise HTTPException(status_code=400, detail="Room is required.")
    if payload.category not in (None, "oral", "poster"):
        raise HTTPException(status_code=400, detail="Category must be oral or poster.")

    selected = set(payload.abstract_ids)
    candidates = [
        c for c in _load_presenter_candidates(db, event_id, with_slides_only=True)
        if c["abstract_id"] in selected
    ]
    if not candidates:
        raise HTTPException(status_code=404, detail="None of the selected presenters have an uploaded presentation.")

    max_order = db.query(func.max(ProgrammeEntry.sort_order)).filter(
        ProgrammeEntry.event_id == event_id, ProgrammeEntry.deleted_at == None,
    ).scalar() or 0

    created, updated = 0, 0
    for c in candidates:
        category = payload.category
        if not category:
            category = "poster" if c["presentation_type"] == "poster" else "oral"
        name = " ".join(p for p in [(c["first"] or "").strip(), (c["last"] or "").strip()] if p)
        existing = db.query(ProgrammeEntry).filter(
            ProgrammeEntry.abstract_id == c["abstract_id"],
            ProgrammeEntry.event_id == event_id,
            ProgrammeEntry.deleted_at == None,
        ).first()
        if existing:
            existing.room = room
            existing.day = payload.day or "Day 1"
            if payload.session is not None:
                existing.session = payload.session
            existing.category = category
            existing.title = c["title"]
            existing.presenter_name = name
            updated += 1
        else:
            max_order += 1
            db.add(ProgrammeEntry(
                event_id=event_id,
                category=category,
                day=payload.day or "Day 1",
                session=payload.session,
                room=room,
                title=c["title"],
                presenter_name=name,
                abstract_id=c["abstract_id"],
                sort_order=max_order,
            ))
            created += 1
    db.commit()
    return {
        "detail": f"Assigned {created} new and moved {updated}.",
        "created": created,
        "updated": updated,
    }


# ── Room-leader view (public, shareable link) ─────────────────────────────────
@router.get("/room-view")
def room_view(
    db: Session = Depends(get_db),
    event_id: int = Query(DEFAULT_EVENT_ID),
    day: str = Query(...),
    room: str = Query(...),
):
    """Read-only running order for one room/day, for the admin to share with
    that room's session leader/moderator.

    Public-by-URL (no JWT, no PIN, no admin permission check) — same trust
    model as the presentation preview/download/zip links below: the admin
    generates and shares this URL, and it always reflects live data (nothing
    is cached or exported), so reloading it after new slides are uploaded or
    presenters get matched shows the update immediately.
    """
    entries = (
        db.query(ProgrammeEntry)
        .options(joinedload(ProgrammeEntry.abstract))
        .filter(
            ProgrammeEntry.event_id == event_id,
            ProgrammeEntry.deleted_at == None,
            ProgrammeEntry.day == day,
            ProgrammeEntry.room == room,
        )
        .order_by(ProgrammeEntry.session.asc(), ProgrammeEntry.sort_order.asc())
        .all()
    )
    event = db.query(Event).filter(Event.id == event_id).first()
    return {
        "event": {"id": event.id, "name": event.event} if event else None,
        "day": day,
        "room": room,
        "entries": [_serialize_base(e) for e in entries],
    }


# ── Matching programme slots to submitted Abstracts ──────────────────────────
@router.get("/match-abstracts")
def match_abstracts_preview(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(DEFAULT_EVENT_ID),
    category: str = Query("oral"),
):
    """Dry-run: proposes presenter-name corrections + abstract links for every
    programme entry of `category`, matched by presenter name against accepted
    Abstracts (title text is intentionally ignored — see _compute_abstract_matches).
    Nothing is written; call POST .../match-abstracts/apply to commit."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    return _compute_abstract_matches(db, event_id, category)


class ApplyMatchesSchema(BaseModel):
    # Which proposed matches (by entry_id) to actually write — lets the admin
    # review each one (and check the presenter's uploaded slides for the
    # matched abstract, when there is one) before committing rather than
    # applying the whole batch blind. None (the default — no body, or
    # entry_ids omitted) applies every proposed match, same as before this
    # existed; an explicit list, including an empty one, applies only those.
    entry_ids: Optional[List[int]] = None


@router.post("/match-abstracts/apply")
def match_abstracts_apply(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    payload: ApplyMatchesSchema = ApplyMatchesSchema(),
    event_id: int = Query(DEFAULT_EVENT_ID),
    category: str = Query("oral"),
):
    """Recomputes the same matches as the preview and writes the selected
    ones: each gets abstract_id set and its presenter_name corrected to the
    name on file for the abstract's presenting author."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    report = _compute_abstract_matches(db, event_id, category)
    to_apply = report["matches"]
    if payload.entry_ids is not None:
        selected = set(payload.entry_ids)
        to_apply = [m for m in to_apply if m["entry_id"] in selected]
    entry_ids = [m["entry_id"] for m in to_apply]
    entries_by_id = {
        e.id: e for e in
        db.query(ProgrammeEntry).filter(ProgrammeEntry.id.in_(entry_ids)).all()
    } if entry_ids else {}
    renamed = 0
    linked = 0
    for m in to_apply:
        entry = entries_by_id.get(m["entry_id"])
        if not entry:
            continue
        if entry.abstract_id != m["abstract_id"]:
            entry.abstract_id = m["abstract_id"]
            linked += 1
        if m["corrected_name"] and entry.presenter_name != m["corrected_name"]:
            entry.presenter_name = m["corrected_name"]
            renamed += 1
    db.commit()
    return {
        "applied": len(to_apply),
        "skipped": len(report["matches"]) - len(to_apply),
        "renamed": renamed,
        "linked": linked,
        "unmatched_entries": len(report["unmatched_entries"]),
        "unmatched_abstracts": len(report["unmatched_abstracts"]),
    }


class LinkAbstractSchema(BaseModel):
    abstract_id: int


@router.put("/{entry_id}/link-abstract")
def link_abstract(
    entry_id: int,
    payload: LinkAbstractSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    """Manual pairing for the ones the automatic matcher couldn't place —
    picked from the report's unmatched-abstracts list. Also corrects the
    presenter name to the one on file, same as the automatic match."""
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    entry = db.query(ProgrammeEntry).filter(
        ProgrammeEntry.id == entry_id, ProgrammeEntry.deleted_at == None,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    abstract = db.query(Abstract).filter(
        Abstract.id == payload.abstract_id, Abstract.deleted_at == None,
    ).first()
    if not abstract:
        raise HTTPException(status_code=404, detail="Abstract not found")
    authors = (
        db.query(AbstractAuthor)
        .filter(AbstractAuthor.abstract_id == abstract.id)
        .order_by(AbstractAuthor.author_order.asc())
        .all()
    )
    presenting = next((a for a in authors if a.is_presenting), authors[0] if authors else None)
    entry.abstract_id = abstract.id
    if presenting:
        name = " ".join(p for p in [(presenting.firstname or "").strip(), (presenting.lastname or "").strip()] if p)
        if name:
            entry.presenter_name = name
    db.commit()
    db.refresh(entry)
    reg_rows = _load_reg_rows(db, entry.event_id)
    m = best_registration_match(entry.presenter_name or "", reg_rows)
    return _serialize(entry, m)


@router.delete("/{entry_id}/link-abstract")
def unlink_abstract(
    entry_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    entry = db.query(ProgrammeEntry).filter(
        ProgrammeEntry.id == entry_id, ProgrammeEntry.deleted_at == None,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    entry.abstract_id = None
    db.commit()
    db.refresh(entry)
    reg_rows = _load_reg_rows(db, entry.event_id)
    m = best_registration_match(entry.presenter_name or "", reg_rows)
    return _serialize(entry, m)


# ── Create / Update / Delete ────────────────────────────────────────────────
class ProgrammeEntrySch(BaseModel):
    category: Optional[str] = None
    day: Optional[str] = None
    session: Optional[str] = None
    room: Optional[str] = None
    code: Optional[str] = None
    theme: Optional[str] = None
    title: Optional[str] = None
    presenter_name: Optional[str] = None
    role: Optional[str] = None
    activity: Optional[str] = None
    original_presenter: Optional[str] = None
    is_substitution: Optional[bool] = None
    notes: Optional[str] = None


@router.post("")
def create_entry(
    payload: ProgrammeEntrySch,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    event_id: int = Query(DEFAULT_EVENT_ID),
    day: str = Query(None),
    category: str = Query("oral"),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    if not payload.presenter_name:
        raise HTTPException(status_code=400, detail="presenter_name is required.")
    max_order = db.query(func.max(ProgrammeEntry.sort_order)).filter(
        ProgrammeEntry.event_id == event_id, ProgrammeEntry.deleted_at == None,
    ).scalar() or 0
    entry = ProgrammeEntry(
        event_id=event_id,
        category=payload.category or category,
        day=payload.day or day or "Day 1",
        session=payload.session,
        room=payload.room,
        code=payload.code,
        theme=payload.theme,
        title=payload.title,
        presenter_name=payload.presenter_name,
        role=payload.role,
        activity=payload.activity,
        original_presenter=payload.original_presenter,
        is_substitution=bool(payload.is_substitution),
        notes=payload.notes,
        sort_order=max_order + 1,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _serialize(entry)


@router.put("/{entry_id}")
def update_entry(
    entry_id: int,
    payload: ProgrammeEntrySch,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    entry = db.query(ProgrammeEntry).filter(
        ProgrammeEntry.id == entry_id, ProgrammeEntry.deleted_at == None,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    # Rename presenters with explicit substitution bookkeeping. A plain name
    # change (is_substitution False) is a correction; only when the caller flags
    # a substitution is the previous name preserved as original_presenter.
    if payload.presenter_name is not None and payload.presenter_name != entry.presenter_name:
        is_sub = bool(payload.is_substitution)
        if is_sub:
            if not entry.original_presenter:
                entry.original_presenter = entry.presenter_name
            entry.is_substitution = True
        entry.presenter_name = payload.presenter_name
    for field in ("category", "day", "session", "room", "code", "theme", "title",
                  "role", "activity", "original_presenter", "notes"):
        value = getattr(payload, field)
        if value is not None:
            setattr(entry, field, value)
    if payload.is_substitution is not None:
        entry.is_substitution = payload.is_substitution
    if payload.is_substitution is False and payload.presenter_name is None:
        # explicit clear of the substitution flag without a rename
        entry.is_substitution = False
    db.commit()
    db.refresh(entry)
    reg_rows = _load_reg_rows(db, entry.event_id)
    m = best_registration_match(entry.presenter_name or "", reg_rows)
    return _serialize(entry, m)


@router.delete("/{entry_id}")
def delete_entry(
    entry_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    entry = db.query(ProgrammeEntry).filter(
        ProgrammeEntry.id == entry_id, ProgrammeEntry.deleted_at == None,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    from datetime import datetime, timezone
    entry.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"detail": "Entry removed."}


# ── Slide upload ─────────────────────────────────────────────────────────────
@router.delete("/{entry_id}/presentation")
def remove_presentation(
    entry_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    entry = db.query(ProgrammeEntry).filter(
        ProgrammeEntry.id == entry_id, ProgrammeEntry.deleted_at == None,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    if entry.presentation_file and os.path.exists(entry.presentation_file):
        try:
            os.remove(entry.presentation_file)
        except OSError:
            pass
    entry.presentation_file = None
    entry.presentation_uploaded_at = None
    db.commit()
    return {"detail": "Presentation removed."}


@router.post("/{entry_id}/upload-presentation")
async def upload_presentation(
    entry_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
    file: UploadFile = File(...),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    entry = db.query(ProgrammeEntry).filter(
        ProgrammeEntry.id == entry_id, ProgrammeEntry.deleted_at == None,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    ext = os.path.splitext(file.filename or "")[-1].lower()
    if ext not in ALLOWED_PRESENTATION_EXTS:
        raise HTTPException(status_code=400, detail=f"Allowed types: {', '.join(sorted(ALLOWED_PRESENTATION_EXTS))}")
    content = await file.read()
    if len(content) > MAX_PRESENTATION_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File must be under {MAX_PRESENTATION_MB} MB")
    if entry.presentation_file and os.path.exists(entry.presentation_file):
        try:
            os.remove(entry.presentation_file)
        except OSError:
            pass
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(PROGRAMME_UPLOAD_DIR, stored_name)
    with open(stored_path, "wb") as fh:
        fh.write(content)
    from datetime import datetime, timezone
    entry.presentation_file = stored_path
    entry.presentation_uploaded_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Presentation uploaded successfully", "filename": file.filename,
            "entry_id": entry_id, "presentation_file": stored_path}


# ── Preview / download (PIN-protected) ───────────────────────────────────────
@router.get("/{entry_id}/preview-presentation")
def preview_presentation(
    entry_id: int,
    db: Session = Depends(get_db),
):
    """Serve slides inline for browser preview.

    Public-by-URL (no JWT, no PIN) — same model as the abstract preview links:
    the admin generates this URL and shares it, so the Office Online viewer can
    fetch it and anyone with the link can view the slides. Falls back to the
    linked abstract's own uploaded file if nothing's been uploaded here.
    """
    entry = db.query(ProgrammeEntry).options(joinedload(ProgrammeEntry.abstract)).filter(
        ProgrammeEntry.id == entry_id, ProgrammeEntry.deleted_at == None,
    ).first()
    path = _effective_presentation_file(entry) if entry else None
    if not path:
        raise HTTPException(status_code=404, detail="No presentation file found")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found on server")
    ext = os.path.splitext(path)[-1].lower()
    media_type = PREVIEW_MEDIA_TYPES.get(ext)
    if not media_type:
        raise HTTPException(status_code=415, detail="Preview not supported for this file type")
    return FileResponse(path=path, media_type=media_type)


@router.get("/{entry_id}/download-presentation")
def download_presentation(
    entry_id: int,
    db: Session = Depends(get_db),
):
    """Serve the slides file for direct download.

    Public-by-URL (no JWT, no PIN) — mirrors the abstract file links: the admin
    generates this URL in the dashboard and shares it, so anyone with the URL
    can fetch the file. This is also why the whole-room ZIP is public-by-URL
    below. Falls back to the linked abstract's own uploaded file if nothing's
    been uploaded here.
    """
    entry = db.query(ProgrammeEntry).options(joinedload(ProgrammeEntry.abstract)).filter(
        ProgrammeEntry.id == entry_id, ProgrammeEntry.deleted_at == None,
    ).first()
    path = _effective_presentation_file(entry) if entry else None
    if not path:
        raise HTTPException(status_code=404, detail="No presentation file found")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found on server")
    ext = os.path.splitext(path)[-1]
    label = re.sub(r"[^A-Za-z0-9 _-]+", "", (entry.presenter_name or "")).strip().replace(" ", "_")[:40] or f"entry_{entry.id}"
    return FileResponse(path=path, filename=f"{label}_{entry.id}{ext}",
                        media_type="application/octet-stream")


@router.get("/download-room-zip")
def download_room_zip(
    db: Session = Depends(get_db),
    event_id: int = Query(DEFAULT_EVENT_ID),
    room: str = Query(None),
    day: str = Query(None),
):
    """Serve all slides for a room/day as one ZIP.

    Public-by-URL (no JWT, no PIN) — same trust model as the abstract links
    and the whole-office ZIP page: the admin generates this URL in the
    dashboard and shares it, so anyone with the URL can fetch the ZIP. Includes
    a slot's linked-abstract file when nothing's been uploaded to the slot
    itself.
    """
    q = db.query(ProgrammeEntry).options(joinedload(ProgrammeEntry.abstract)).filter(
        ProgrammeEntry.event_id == event_id,
        ProgrammeEntry.deleted_at == None,
    )
    if room:
        q = q.filter(ProgrammeEntry.room == room)
    if day:
        q = q.filter(ProgrammeEntry.day == day)
    entries = q.order_by(ProgrammeEntry.sort_order.asc()).all()
    if not entries:
        raise HTTPException(status_code=404, detail="No slides found for this room/day.")

    buf = io.BytesIO()
    added = 0
    used = set()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for e in entries:
            path = _effective_presentation_file(e)
            if not path or not os.path.exists(path):
                continue
            ext = os.path.splitext(path)[-1]
            base = re.sub(r"[^A-Za-z0-9 _-]+", "", (e.code or e.presenter_name or str(e.id))).strip()[:60] or f"entry_{e.id}"
            arc = f"{base}{ext}"
            n = 1
            while arc in used:
                n += 1
                arc = f"{base}_{n}{ext}"
            used.add(arc)
            zf.write(path, arcname=arc)
            added += 1
    if added == 0:
        raise HTTPException(status_code=404, detail="No slide files were found on disk for this room/day.")
    buf.seek(0)
    label = f"_{room}" if room else ""
    filename = f"room{label}_slides.zip"
    return StreamingResponse(
        buf, media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )