"""
Seed / re-seed the conference programme timetable (programme_entry rows).

Idempotent: upserts by (event_id, category, day, code/activity, presenter_name).
Run from the api directory with the project venv:
    venv/bin/python seed_programme.py
Data source: api/assets/programme_data.json (generated from the official programme).
"""
import os
import json
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.models import ProgrammeEntry

DATA_FILE = os.path.join(os.path.dirname(__file__), "assets", "programme_data.json")


def _key(row: dict) -> tuple:
    identity = row.get("code") or row.get("activity") or row.get("title") or ""
    # Title varies in length; code/activity is the stable programme reference.
    return (row["category"], row["day"], identity.strip().lower()[:120])


def seed() -> None:
    with open(DATA_FILE, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    event_id = int(data.get("event_id", 1))
    rows = data.get("entries", [])

    db: Session = SessionLocal()
    try:
        existing = {_key(r): r.id for r in db.query(ProgrammeEntry).filter(
            ProgrammeEntry.event_id == event_id,
            ProgrammeEntry.deleted_at == None,
        ).all()}
        existing_names = {}  # (category, day, code) -> id to also catch renames
        for r in db.query(ProgrammeEntry).filter(
            ProgrammeEntry.event_id == event_id,
            ProgrammeEntry.deleted_at == None,
        ).all():
            existing_names[(r.category, r.day, r.code or r.activity or "")] = r.id

        created, updated = 0, 0
        for idx, row in enumerate(rows):
            ident = (row["category"], row["day"], (row.get("code") or row.get("activity") or row.get("title") or "").strip().lower()[:120])
            row_id = existing.get(ident) or existing_names.get(
                (row["category"], row["day"], row.get("code") or row.get("activity") or "")
            )
            sort_order = idx
            if row_id:
                entry = db.query(ProgrammeEntry).filter(ProgrammeEntry.id == row_id).first()
                changed = False
                for field in ("title", "role", "activity", "room", "session", "theme"):
                    if getattr(entry, field) != row.get(field):
                        setattr(entry, field, row.get(field))
                        changed = True
                if entry.sort_order != sort_order:
                    entry.sort_order = sort_order
                    changed = True
                # Never revert a live "presenter_name" substitution made in the
                # system back to the seed data — re-seeding should be safe to run.
                if not entry.is_substitution and entry.presenter_name != row.get("presenter_name"):
                    entry.presenter_name = row.get("presenter_name")
                    changed = True
                if changed:
                    updated += 1
            else:
                entry = ProgrammeEntry(
                    event_id=event_id,
                    category=row["category"],
                    day=row["day"],
                    session=row.get("session"),
                    room=row.get("room"),
                    code=row.get("code"),
                    theme=row.get("theme"),
                    title=row.get("title"),
                    presenter_name=row.get("presenter_name"),
                    role=row.get("role"),
                    activity=row.get("activity"),
                    original_presenter=row.get("original_presenter"),
                    is_substitution=bool(row.get("is_substitution", False)),
                    notes=row.get("notes"),
                    sort_order=sort_order,
                )
                db.add(entry)
                created += 1
        db.commit()
        print(f"Seeded programme for event {event_id}: {created} created, {updated} updated (total {len(rows)} entries).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()