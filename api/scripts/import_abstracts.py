import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import mysql.connector
from urllib.parse import quote_plus

MYSQL_HOSTNAME = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DB = "ecsaconm_events"
EVENT_ID = 1
ODS_FILE = "/Users/davishyacinth/Downloads/All-Abstracts.xlsx.ods"

conn = mysql.connector.connect(
    host=MYSQL_HOSTNAME,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB,
    unix_socket="/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock",
    charset="utf8mb4"
)
cursor = conn.cursor()

df = pd.read_excel(ODS_FILE, engine="odf")

existing_emails_q = "SELECT id, LOWER(TRIM(email)) AS email FROM user"
cursor.execute(existing_emails_q)
user_by_email = {row[1]: row[0] for row in cursor.fetchall()}

existing_abstracts_q = "SELECT title FROM abstract WHERE event_id = %s"
cursor.execute(existing_abstracts_q, (EVENT_ID,))
existing_titles = {row[0] for row in cursor.fetchall()}


def parse_name(full_name):
    parts = (full_name or "").strip().rsplit(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return (full_name or "").strip(), ""


def parse_author_name(raw):
    name = str(raw).strip()
    if "|" in name:
        name = name.split("|")[0].strip()
    return parse_name(name)


def parse_presenter_name(raw):
    name = str(raw).strip()
    return parse_name(name)


imported = 0
skipped = 0
errors = 0

for _, row in df.iterrows():
    title = str(row.get("Title") or "").strip()
    if not title:
        skipped += 1
        continue
    if title in existing_titles:
        skipped += 1
        continue

    abstract_text = str(row.get("Description") or "").strip()
    track = str(row.get("Topic") or "").strip()
    keywords = str(row.get("Keywords") or "").strip()
    status_raw = str(row.get("Status") or "").strip()
    presentation_type = "oral" if "oral" in status_raw.lower() else "poster"
    status = "accepted"
    word_count = len(abstract_text.split()) if abstract_text else 0

    presenter_email = str(row.get("Presenter Email") or "").strip().lower()
    submitter_id = user_by_email.get(presenter_email, 1)

    try:
        cursor.execute(
            """INSERT INTO abstract
               (event_id, submitted_by, title, abstract_text, keywords, track,
                presentation_type, status, word_count, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
            (EVENT_ID, submitter_id, title, abstract_text, keywords, track,
             presentation_type, status, word_count),
        )
        abstract_id = cursor.lastrowid

        authors = []
        first_author_raw = row.get("Author Name")
        if pd.notna(first_author_raw):
            fn, ln = parse_author_name(first_author_raw)
            authors.append({
                "firstname": fn, "lastname": ln,
                "email": presenter_email if presenter_email else None,
                "affiliation": str(row.get("Author Affiliation") or "").strip() or None,
                "country": None, "is_presenting": True,
            })

        presenter_name_raw = row.get("Presenter Name")
        if pd.notna(presenter_name_raw):
            pfn, pln = parse_presenter_name(presenter_name_raw)
            if not authors or (authors[0]["firstname"].lower(), authors[0]["lastname"].lower()) != (pfn.lower(), pln.lower()):
                authors.append({
                    "firstname": pfn, "lastname": pln,
                    "email": presenter_email if presenter_email else None,
                    "affiliation": str(row.get("Author Affiliation") or "").strip() or None,
                    "country": None, "is_presenting": True,
                })

        for i in range(1, 9):
            col = f"Author Email_{i}"
            if col not in row.index:
                continue
            em = str(row.get(col) or "").strip()
            if not em or em.lower() == "nan":
                continue
            em_lower = em.lower()
            if any(a.get("email") == em_lower for a in authors):
                continue
            authors.append({
                "firstname": em.split("@")[0].replace(".", " ").title(),
                "lastname": "", "email": em_lower,
                "affiliation": None, "country": None, "is_presenting": False,
            })

        for order, au in enumerate(authors):
            cursor.execute(
                """INSERT INTO abstract_author
                   (abstract_id, firstname, lastname, email, affiliation, country,
                    is_presenting, author_order, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                (abstract_id, au["firstname"], au["lastname"], au["email"],
                 au["affiliation"], au["country"], au["is_presenting"], order),
            )

        conn.commit()
        existing_titles.add(title)
        imported += 1
        if imported % 20 == 0:
            print(f"  Imported {imported} abstracts...")

    except Exception as e:
        conn.rollback()
        errors += 1
        print(f"  ERROR importing '{title[:50]}': {e}")

cursor.close()
conn.close()

print(f"\nDone! Imported: {imported}, Skipped: {skipped}, Errors: {errors}")
