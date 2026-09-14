import os
import re
import io
import uuid
import hmac
import zipfile
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Header
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from core.database import get_db
from dependencies.auth_dependency import Auth, get_current_user
from models.models import ProgrammeEntry, SystemSetting, User, Registration

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]

ROOM_PIN_KEY = "programme_room_pin"
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
    return "".join(p[:-1])


def best_registration_match(pname, reg_rows):
    """reg_rows: list of dicts {user_id, first, last, is_paid}. Mirrors the JS bestMatch."""
    sn, fn = _surname(pname), _firstname(pname)
    best, best_score = None, -1
    for r in reg_rows:
        rsn = _norm(r["last"] or "")
        rfn = _norm(r["first"] or "")
        if not rsn:
            continue
        if not (rsn == sn or (len(rsn) >= 5 and rsn[:4] == sn[:4])):
            continue
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
        if sc > best_score:
            best_score = sc
            best = r
    if not best or best_score < 3:
        return None
    return {"id": best["user_id"], "first": best["first"], "last": best["last"],
            "paid": best["is_paid"], "score": best_score}


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


def _pin_setting(db: Session) -> str:
    row = db.query(SystemSetting).filter(SystemSetting.key == ROOM_PIN_KEY).first()
    return (row.value or "") if row else ""


def _require_pin(db: Session, pin: str):
    if not pin:
        raise HTTPException(status_code=401, detail="Room PIN is required.")
    stored = _pin_setting(db)
    if not stored:
        raise HTTPException(status_code=409, detail="No room PIN has been set yet.")
    if not hmac.compare_digest(pin.strip(), stored):
        raise HTTPException(status_code=403, detail="Invalid room PIN.")


def _serialize(entry: ProgrammeEntry, match=None):
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
        "presentation_file": entry.presentation_file,
        "presentation_uploaded_at": entry.presentation_uploaded_at.isoformat() if entry.presentation_uploaded_at else None,
        "sort_order": entry.sort_order,
        # live registration / payment status
        "status": "registered_paid" if match and match["paid"] else (
            "registered_unpaid" if match else "not_registered"),
        "registered": bool(match),
        "paid": bool(match and match["paid"]),
        "match_score": match["score"] if match else None,
        "matched_user_id": match["id"] if match else None,
        "matched_first": match["first"] if match else None,
        "matched_last": match["last"] if match else None,
    }


# ── PIN management ───────────────────────────────────────────────────────────
@router.get("/pin/status")
def pin_status(
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    return {"set": bool(_pin_setting(db))}


class PinSetSchema(BaseModel):
    pin: str


@router.put("/pin")
def pin_set(
    payload: PinSetSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    pin = payload.pin.strip()
    if len(pin) < 4:
        raise HTTPException(status_code=400, detail="PIN must be at least 4 characters.")
    row = db.query(SystemSetting).filter(SystemSetting.key == ROOM_PIN_KEY).first()
    if row:
        row.value = pin
    else:
        db.add(SystemSetting(key=ROOM_PIN_KEY, value=pin))
    db.commit()
    return {"detail": "Rooms PIN updated."}


@router.post("/pin/verify")
def pin_verify(
    payload: PinSetSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    auth_dependency: Auth = Depends(get_auth_dep),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    stored = _pin_setting(db)
    if not stored:
        raise HTTPException(status_code=409, detail="No room PIN has been set yet.")
    if hmac.compare_digest(payload.pin.strip(), stored):
        return {"valid": True}
    return {"valid": False}


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
    q = db.query(ProgrammeEntry).filter(
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
    pin: str = Query(None),
    x_room_pin: Optional[str] = Header(None),
):
    auth_dependency.secure_access("ADMIN_DASHBOARD", current_user["user_id"])
    _require_pin(db, pin or x_room_pin or "")
    entries = db.query(ProgrammeEntry).filter(
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
        if e.presentation_file:
            bucket["with_slide"] += 1
        bucket["entries"].append(_serialize(e, cache.get(key)))
    result = []
    for (day, room), bucket in sorted(rooms.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        bucket["entries"].sort(key=lambda x: (x["session"] or "", x["code"] or "", x["title"] or ""))
        result.append({"day": bucket["day"], "room": bucket["room"], "total": bucket["total"],
                        "with_slide": bucket["with_slide"], "entries": bucket["entries"]})
    return {"data": result}


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
    fetch it and anyone with the link can view the slides.
    """
    entry = db.query(ProgrammeEntry).filter(
        ProgrammeEntry.id == entry_id, ProgrammeEntry.deleted_at == None,
    ).first()
    if not entry or not entry.presentation_file:
        raise HTTPException(status_code=404, detail="No presentation file found")
    if not os.path.exists(entry.presentation_file):
        raise HTTPException(status_code=404, detail="File not found on server")
    ext = os.path.splitext(entry.presentation_file)[-1].lower()
    media_type = PREVIEW_MEDIA_TYPES.get(ext)
    if not media_type:
        raise HTTPException(status_code=415, detail="Preview not supported for this file type")
    return FileResponse(path=entry.presentation_file, media_type=media_type)


@router.get("/{entry_id}/download-presentation")
def download_presentation(
    entry_id: int,
    db: Session = Depends(get_db),
):
    """Serve the slides file for direct download.

    Public-by-URL (no JWT, no PIN) — mirrors the abstract file links: the admin
    generates this URL in the dashboard and shares it, so anyone with the URL
    can fetch the file. This is also why the whole-room ZIP is public-by-URL
    below.
    """
    entry = db.query(ProgrammeEntry).filter(
        ProgrammeEntry.id == entry_id, ProgrammeEntry.deleted_at == None,
    ).first()
    if not entry or not entry.presentation_file:
        raise HTTPException(status_code=404, detail="No presentation file found")
    if not os.path.exists(entry.presentation_file):
        raise HTTPException(status_code=404, detail="File not found on server")
    ext = os.path.splitext(entry.presentation_file)[-1]
    label = re.sub(r"[^A-Za-z0-9 _-]+", "", (entry.presenter_name or "")).strip().replace(" ", "_")[:40] or f"entry_{entry.id}"
    return FileResponse(path=entry.presentation_file, filename=f"{label}_{entry.id}{ext}",
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
    dashboard and shares it, so anyone with the URL can fetch the ZIP.
    """
    q = db.query(ProgrammeEntry).filter(
        ProgrammeEntry.event_id == event_id,
        ProgrammeEntry.deleted_at == None,
        ProgrammeEntry.presentation_file != None,
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
            if not e.presentation_file or not os.path.exists(e.presentation_file):
                continue
            ext = os.path.splitext(e.presentation_file)[-1]
            base = re.sub(r"[^A-Za-z0-9 _-]+", "", (e.code or e.presenter_name or str(e.id))).strip()[:60] or f"entry_{e.id}"
            arc = f"{base}{ext}"
            n = 1
            while arc in used:
                n += 1
                arc = f"{base}_{n}{ext}"
            used.add(arc)
            zf.write(e.presentation_file, arcname=arc)
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