"""
Seed/refresh the email_template table from the HTML template files in
./templates. The Email Templates admin section (Configurations → Email
Templates) only lists rows present in this table, so until this runs it is
empty and no template can be edited from the UI. Idempotent — upserts by
template_key, so it can be re-run safely after editing a file to refresh
the DB copy.

Run from the api directory: python seed_email_templates.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session  # noqa: E402
from core.database import SessionLocal  # noqa: E402
from models.models import EmailTemplate  # noqa: E402

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

# template_key -> metadata. body_html is read from the matching file in
# ./templates. Keep the keys and filenames in sync with
# routers/email_templates.py's fname_map so edits made in the UI sync back
# to the same file.
TEMPLATES = {
    "account_creation": {
        "name": "Account Creation",
        "subject": "Welcome to ECSACONM Events Portal – Activate Your Account",
        "file": "acount_creation_template.html",
        "variables": "username, password, firstname, event_name, year",
    },
    "password_reset_request": {
        "name": "Password Reset Request",
        "subject": "Password Reset Request",
        "file": "password_reset_request_template.html",
        "variables": "username, firstname, reset_token, reset_link, year",
    },
    "password_reset": {
        "name": "Password Reset",
        "subject": "Your ECSACONM Events Portal password has been reset",
        "file": "password_reset_template.html",
        "variables": "firstname, email, year",
    },
    "account_verification_request": {
        "name": "Account Verification Request",
        "subject": "Account Verification Request",
        "file": "account_verification_request_template.html",
        "variables": "email, firstname, verification_token, year",
    },
    "account_verification": {
        "name": "Account Verification",
        "subject": "Your ECSACONM Events Portal account has been verified",
        "file": "account_verification_template.html",
        "variables": "email, firstname, year",
    },
    "organisation_verification_request": {
        "name": "Organisation Verification Request",
        "subject": "Organisation Verification Request",
        "file": "organisation_verification_request_template.html",
        "variables": "email, firstname, organisation, organisation_id, year",
    },
    "organisation_approval_status": {
        "name": "Organisation Approval Status",
        "subject": "Organisation Approval Status",
        "file": "organisation_approval_status_template.html",
        "variables": "email, firstname, organisation, organisation_id, status, year",
    },
    "registration_reminder": {
        "name": "Registration Reminder",
        "subject": "Reminder: Register for {event_name}",
        "file": "registration_reminder_template.html",
        "variables": "subject, firstname, event_name, abstract_title, has_account, year",
    },
    "reviewer_assignment": {
        "name": "Reviewer Assignment",
        "subject": "You Have Been Assigned an Abstract to Review – ECSACONM Events Portal",
        "file": "reviewer_assignment_template.html",
        "variables": "username, firstname, password, abstract_title, event_name, year",
    },
    "abstract_submission_deadline": {
        "name": "Abstract Submission Deadline Reminder",
        "subject": "Reminder: Abstract Submission Deadline is Today",
        "file": "abstract_submission_deadline_template.html",
        "variables": "subject, firstname, event_name, year",
    },
}


def seed():
    db: Session = SessionLocal()
    created = 0
    updated = 0
    try:
        for key, meta in TEMPLATES.items():
            fpath = os.path.join(TEMPLATES_DIR, meta["file"])
            if not os.path.exists(fpath):
                print(f"⚠ skipped {key}: missing file {meta['file']}")
                continue
            with open(fpath, "r", encoding="utf-8") as f:
                body_html = f.read()

            t = db.query(EmailTemplate).filter_by(template_key=key).first()
            if t:
                t.name = meta["name"]
                t.subject = meta["subject"]
                t.body_html = body_html
                t.variables = meta["variables"]
                updated += 1
            else:
                db.add(EmailTemplate(
                    template_key=key,
                    name=meta["name"],
                    subject=meta["subject"],
                    body_html=body_html,
                    variables=meta["variables"],
                ))
                created += 1
        db.commit()
        print(f"✓ {created} created, {updated} updated, {len(TEMPLATES)} templates in the email_template table")
    except Exception as e:
        db.rollback()
        print(f"✗ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()