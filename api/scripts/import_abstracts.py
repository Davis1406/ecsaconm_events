"""
Import accepted abstracts from an ODS spreadsheet into the ECSACONM Events database.

Reads the file at the configured path, maps columns to the abstract and
abstract_author tables, creates user accounts for presenters who don't have one
yet, and assigns the abstract's submitted_by to the matching user.

Idempotent: skips abstracts that already exist (matched by title + event_id).

Usage:
    cd api/
    python scripts/import_abstracts.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from sqlalchemy.orm import Session

from core.database import SessionLocal
from models.models import Abstract, AbstractAuthor, User, UserRole, Role

# ── Configuration ────────────────────────────────────────────────────────────
ODS_FILE = "/Users/davishyacinth/Downloads/All-Abstracts.xlsx.ods"
EVENT_ID = 1
ADMIN_USER_ID = 1
ABSTRACT_STATUS = "accepted"


def parse_name(full_name: str) -> tuple[str, str]:
    """Split a full name into (firstname, lastname).
    Splits on the last space: everything before = firstname, last token = lastname.
    """
    if not full_name or not isinstance(full_name, str):
        return ("", "")
    parts = full_name.strip().split()
    if len(parts) == 0:
        return ("", "")
    if len(parts) == 1:
        return (parts[0], "")
    firstname = " ".join(parts[:-1])
    lastname = parts[-1]
    return (firstname, lastname)


def map_status(status_str: str) -> tuple[str, str]:
    """Map the spreadsheet status to (db_status, presentation_type)."""
    if not isinstance(status_str, str):
        return (ABSTRACT_STATUS, "either")
    lower = status_str.strip().lower()
    if "oral" in lower:
        return ("accepted", "oral")
    if "poster" in lower:
        return ("accepted", "poster")
    return (ABSTRACT_STATUS, "either")


def get_or_create_user(db: Session, email: str, firstname: str, lastname: str) -> User | None:
    """Find existing user by email, or create a new one. Returns the User."""
    if not email or not isinstance(email, str):
        return None
    email = email.strip().lower()
    if not email:
        return None

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return existing

    # Generate a placeholder phone from email
    phone = f"pending_{email.split('@')[0]}"

    # Avoid phone collisions
    if db.query(User).filter(User.phone == phone).first():
        phone = f"pending_{email.split('@')[0]}_import"

    user = User(
        firstname=firstname or "Unknown",
        lastname=lastname or "",
        email=email,
        phone=phone,
        hashed_password="!",
        verified=False,
    )
    db.add(user)
    db.flush()

    # Assign "User" role so they can eventually log in
    user_role = db.query(Role).filter(Role.role == "User").first()
    if user_role:
        db.add(UserRole(user_id=user.id, role_id=user_role.id))
        db.flush()

    print(f"  [+] Created user account: {firstname} {lastname} <{email}> (id={user.id})")
    return user


def import_abstracts():
    print("\n── Import Abstracts from ODS ──────────────────────────────────")

    if not os.path.exists(ODS_FILE):
        print(f"  ✗  File not found: {ODS_FILE}")
        sys.exit(1)

    print(f"  Reading: {ODS_FILE}")
    df = pd.read_excel(ODS_FILE, engine="odf")
    print(f"  Found {len(df)} rows in spreadsheet")

    # Show column names for debugging
    print(f"  Columns: {list(df.columns)}")

    db = SessionLocal()
    imported = 0
    skipped = 0
    errors = 0
    accounts_created = 0

    try:
        for idx, row in df.iterrows():
            try:
                # ── Extract fields from the spreadsheet ────────────────────────
                title = str(row.get("Title", "")).strip()
                description = str(row.get("Description", "")).strip()
                topic = str(row.get("Topic", "")).strip()
                keywords = str(row.get("Keywords", "")).strip()
                status_raw = str(row.get("Status", ""))

                author_name_raw = str(row.get("Author Name", "")).strip()
                author_affiliation = str(row.get("Author Affiliation", "")).strip()
                presenter_name_raw = str(row.get("Presenter Name", "")).strip()
                presenter_email = str(row.get("Presenter Email", "")).strip()

                if not title or title == "nan":
                    print(f"  [{idx}] Skipping row — no title")
                    skipped += 1
                    continue

                # ── Check for duplicate (idempotent) ──────────────────────────
                existing = db.query(Abstract).filter(
                    Abstract.title == title,
                    Abstract.event_id == EVENT_ID,
                    Abstract.deleted_at == None,
                ).first()
                if existing:
                    print(f"  [{idx}] Skipping (already exists): {title[:60]}…")
                    skipped += 1
                    continue

                # ── Map status ────────────────────────────────────────────────
                status_val, presentation_type = map_status(status_raw)

                # ── Word count ────────────────────────────────────────────────
                word_count = len(description.split()) if description else 0

                # ── Parse presenter name ──────────────────────────────────────
                pres_firstname, pres_lastname = parse_name(
                    presenter_name_raw if presenter_name_raw and presenter_name_raw != "nan"
                    else author_name_raw
                )

                # ── Resolve presenter user account ────────────────────────────
                submitted_by = ADMIN_USER_ID
                if presenter_email and presenter_email != "nan":
                    user = get_or_create_user(
                        db, presenter_email, pres_firstname, pres_lastname
                    )
                    if user:
                        submitted_by = user.id
                        accounts_created += 1

                # ── Create the abstract record ────────────────────────────────
                abstract = Abstract(
                    event_id=EVENT_ID,
                    submitted_by=submitted_by,
                    title=title,
                    abstract_text=description,
                    keywords=keywords if keywords and keywords != "nan" else None,
                    track=topic if topic and topic != "nan" else None,
                    presentation_type=presentation_type,
                    status=status_val,
                    word_count=word_count,
                )
                db.add(abstract)
                db.flush()

                # ── Create author records ─────────────────────────────────────
                author_order = 0

                # 1) First author from "Author Name"
                if author_name_raw and author_name_raw != "nan":
                    a_first, a_last = parse_name(author_name_raw)
                    db.add(AbstractAuthor(
                        abstract_id=abstract.id,
                        firstname=a_first or "Unknown",
                        lastname=a_last or "",
                        email=None,
                        affiliation=author_affiliation if author_affiliation and author_affiliation != "nan" else None,
                        country=None,
                        is_presenting=False,
                        author_order=author_order,
                    ))
                    author_order += 1

                # 2) Presenting author (if different from first author)
                if presenter_name_raw and presenter_name_raw != "nan":
                    p_first, p_last = parse_name(presenter_name_raw)
                    # Only add if different from first author
                    if f"{p_first} {p_last}".strip().lower() != f"{a_first if author_name_raw and author_name_raw != 'nan' else ''} {a_last if author_name_raw and author_name_raw != 'nan' else ''}".strip().lower():
                        db.add(AbstractAuthor(
                            abstract_id=abstract.id,
                            firstname=p_first or "Unknown",
                            lastname=p_last or "",
                            email=presenter_email if presenter_email and presenter_email != "nan" else None,
                            affiliation=author_affiliation if author_affiliation and author_affiliation != "nan" else None,
                            country=None,
                            is_presenting=True,
                            author_order=author_order,
                        ))
                        author_order += 1
                    else:
                        # Same person — mark the first author as presenting
                        # We need to update the just-added author
                        first_author = db.query(AbstractAuthor).filter(
                            AbstractAuthor.abstract_id == abstract.id,
                            AbstractAuthor.author_order == 0,
                        ).first()
                        if first_author:
                            first_author.is_presenting = True
                            first_author.email = presenter_email if presenter_email and presenter_email != "nan" else None
                else:
                    # No presenter specified — mark first author as presenting
                    first_author = db.query(AbstractAuthor).filter(
                        AbstractAuthor.abstract_id == abstract.id,
                        AbstractAuthor.author_order == 0,
                    ).first()
                    if first_author:
                        first_author.is_presenting = True

                # 3) Additional authors from Author Email_1 through Author Email_8
                for i in range(1, 9):
                    col = f"Author Email_{i}"
                    extra_email = str(row.get(col, "")).strip()
                    if extra_email and extra_email != "nan" and extra_email != "None":
                        db.add(AbstractAuthor(
                            abstract_id=abstract.id,
                            firstname="Author",
                            lastname=f"{i}",
                            email=extra_email,
                            affiliation=None,
                            country=None,
                            is_presenting=False,
                            author_order=author_order,
                        ))
                        author_order += 1

                imported += 1
                print(f"  [{idx}] Imported: {title[:70]}…")

            except Exception as e:
                db.rollback()
                errors += 1
                print(f"  [{idx}] ERROR: {e}")
                continue

        # ── Commit all imports ────────────────────────────────────────────────
        db.commit()
        print(f"""
── Summary ──────────────────────────────────────────────
  Imported:      {imported}
  Skipped:       {skipped}
  Errors:        {errors}
  User accounts created: {accounts_created}
──────────────────────────────────────────────────────────
""")
    except Exception as e:
        db.rollback()
        print(f"\n  ✗  Fatal error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import_abstracts()
