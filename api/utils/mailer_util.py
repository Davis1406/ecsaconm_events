import os
import smtplib
import logging
import time
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate, make_msgid
from passlib.context import CryptContext
from starlette.templating import Jinja2Templates
from dotenv import load_dotenv
from fastapi import HTTPException, BackgroundTasks
from datetime import datetime

load_dotenv()

YEAR = datetime.now().year
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

# Public API base used to build the open-tracking pixel URL, e.g.
# "https://events.ecsaconm.org/api" in production or "http://localhost:8001" locally.
API_BASE_URL = os.getenv("BASE_URL", "http://localhost:8001")

# Every outgoing email is CC'd here so there's a visible record of what the
# system has sent, independent of the SMTP account's own (unpopulated, since
# sends go out over raw SMTP rather than through a client that IMAP-appends
# to Sent) mailbox. Override via ADMIN_CC_EMAIL in .env if needed.
ADMIN_CC_EMAIL = os.getenv("ADMIN_CC_EMAIL", "admission@cosecsa.org")


def _cc_recipients(recipient_email):
    """Recipients list for the SMTP envelope: the addressee plus the admin
    CC, deduped so we don't double-send when they happen to be the same."""
    if recipient_email.strip().lower() == ADMIN_CC_EMAIL.strip().lower():
        return [recipient_email]
    return [recipient_email, ADMIN_CC_EMAIL]

# --- PASSWORD UTILS ---


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


# --- CORE EMAIL SENDER ---


logger = logging.getLogger(__name__)


# ── Email log helpers ──────────────────────────────────────────────────────
# mailer_util is called from background tasks as well as request handlers, so
# rather than requiring every caller to thread a SQLAlchemy session through,
# each log write opens (and closes) its own short-lived session.
def _create_email_log(recipient_email, subject, email_type, sent_by_user_id,
                       reply_to_email, body=None):
    """Insert a pending email log entry before sending. Returns the record ID or None."""
    try:
        from core.database import SessionLocal
        from models.models import EmailLog
        db = SessionLocal()
        try:
            record = EmailLog(
                recipient_email=recipient_email,
                subject=subject,
                email_type=email_type,
                sent_by_user_id=sent_by_user_id,
                reply_to_email=reply_to_email,
                status="pending",
                body=body,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record.id
        finally:
            db.close()
    except Exception as log_err:
        logger.error("Failed to create email log entry: %s", log_err)
        return None


def _update_email_log(log_id, status, error_message=None):
    """Update the status of an existing email log entry after the send attempt."""
    if not log_id:
        return
    try:
        from core.database import SessionLocal
        from models.models import EmailLog
        db = SessionLocal()
        try:
            record = db.query(EmailLog).filter(EmailLog.id == log_id).first()
            if record:
                record.status = status
                record.error_message = error_message
                db.commit()
        finally:
            db.close()
    except Exception as log_err:
        logger.error("Failed to update email log entry %s: %s", log_id, log_err)


def _inject_tracking_pixel(email_body, log_id):
    if not log_id:
        return email_body
    pixel = (
        f'<img src="{API_BASE_URL}/email-logs/{log_id}/pixel.png"'
        ' width="1" height="1" style="display:none;" alt="" />'
    )
    if "</body>" in email_body:
        return email_body.replace("</body>", f"{pixel}\n</body>", 1)
    return email_body + pixel


def send_email(recipient_email, subject, email_body, email_type="general",
                sent_by_user_id=None, reply_to_email=None):
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = os.getenv("SMTP_PORT", "")
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if not smtp_host or not smtp_port:
        logger.error("SMTP host and port must be set in environment variables.")
        log_id = _create_email_log(recipient_email, subject, email_type,
                                    sent_by_user_id, reply_to_email, email_body)
        _update_email_log(log_id, "failed", "SMTP not configured")
        return

    try:
        smtp_port = int(smtp_port)
    except ValueError:
        logger.error("SMTP_PORT must be an integer.")
        return

    log_id = _create_email_log(recipient_email, subject, email_type,
                                sent_by_user_id, reply_to_email, email_body)
    final_body = _inject_tracking_pixel(email_body, log_id)

    try:
        from_name = os.getenv("SMTP_FROM_NAME", "ECSACONM Events")
        from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username)
        message = MIMEMultipart("alternative")
        message["From"] = f"{from_name} <{from_email}>"
        message["To"] = recipient_email
        message["Cc"] = ADMIN_CC_EMAIL
        message["Subject"] = subject
        message["Date"] = formatdate(localtime=True)
        message["Message-ID"] = make_msgid(domain="ecsaconm.org")
        message["Reply-To"] = reply_to_email or f"{from_name} <{from_email}>"
        message["X-Mailer"] = "ECSACONM Events Portal"
        message.attach(MIMEText(final_body, "html", "utf-8"))

        envelope_to = _cc_recipients(recipient_email)
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_username, smtp_password)
                server.sendmail(smtp_username, envelope_to, message.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(smtp_username, envelope_to, message.as_string())

        logger.info("Email sent successfully to %s", recipient_email)
        _update_email_log(log_id, "sent")
    except Exception as e:
        logger.error("Failed to send email to %s: %s", recipient_email, str(e))
        _update_email_log(log_id, "failed", str(e))


def send_bulk_emails(jobs, delay_seconds=0.3):
    """Send multiple emails over a single, reused SMTP connection.

    `send_email()` opens (and logs into) a brand-new SMTP connection per
    call, which is fine for one-off emails but not for bulk sends — firing
    dozens/hundreds of near-simultaneous connections at the mail server
    trips connection-flood protection on the receiving end (e.g. CSF
    PORTFLOOD, Exim per-IP limits on shared/cPanel mail hosts), which then
    refuses further connections outright.

    `jobs` is a list of dicts, each with keys:
      recipient_email, subject, email_body, email_type (optional),
      sent_by_user_id (optional), reply_to_email (optional)

    Returns {"sent": int, "failed": int}.
    """
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = os.getenv("SMTP_PORT", "")
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if not smtp_host or not smtp_port:
        logger.error("SMTP host and port must be set in environment variables.")
        for job in jobs:
            log_id = _create_email_log(
                job["recipient_email"], job["subject"], job.get("email_type", "general"),
                job.get("sent_by_user_id"), job.get("reply_to_email"), job["email_body"],
            )
            _update_email_log(log_id, "failed", "SMTP not configured")
        return {"sent": 0, "failed": len(jobs)}

    try:
        smtp_port = int(smtp_port)
    except ValueError:
        logger.error("SMTP_PORT must be an integer.")
        return {"sent": 0, "failed": len(jobs)}

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            server.starttls()
        server.login(smtp_username, smtp_password)
    except Exception as e:
        logger.error("Failed to establish SMTP connection for bulk send: %s", str(e))
        for job in jobs:
            log_id = _create_email_log(
                job["recipient_email"], job["subject"], job.get("email_type", "general"),
                job.get("sent_by_user_id"), job.get("reply_to_email"), job["email_body"],
            )
            _update_email_log(log_id, "failed", str(e))
        return {"sent": 0, "failed": len(jobs)}

    from_name = os.getenv("SMTP_FROM_NAME", "ECSACONM Events")
    from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username)
    sent_count = 0
    failed_count = 0

    try:
        for i, job in enumerate(jobs):
            recipient_email = job["recipient_email"]
            subject = job["subject"]
            email_body = job["email_body"]
            email_type = job.get("email_type", "general")
            sent_by_user_id = job.get("sent_by_user_id")
            reply_to_email = job.get("reply_to_email")

            log_id = _create_email_log(recipient_email, subject, email_type,
                                        sent_by_user_id, reply_to_email, email_body)
            final_body = _inject_tracking_pixel(email_body, log_id)

            try:
                message = MIMEMultipart("alternative")
                message["From"] = f"{from_name} <{from_email}>"
                message["To"] = recipient_email
                message["Cc"] = ADMIN_CC_EMAIL
                message["Subject"] = subject
                message["Date"] = formatdate(localtime=True)
                message["Message-ID"] = make_msgid(domain="ecsaconm.org")
                message["Reply-To"] = reply_to_email or f"{from_name} <{from_email}>"
                message["X-Mailer"] = "ECSACONM Events Portal"
                message.attach(MIMEText(final_body, "html", "utf-8"))

                server.sendmail(smtp_username, _cc_recipients(recipient_email), message.as_string())
                logger.info("Email sent successfully to %s", recipient_email)
                _update_email_log(log_id, "sent")
                sent_count += 1
            except Exception as e:
                logger.error("Failed to send email to %s: %s", recipient_email, str(e))
                _update_email_log(log_id, "failed", str(e))
                failed_count += 1

            # Pace the sends so we don't hammer the mail server even on a
            # single kept-alive connection — some providers rate-limit by
            # messages/sec in addition to connections/sec.
            if delay_seconds and i < len(jobs) - 1:
                time.sleep(delay_seconds)
    finally:
        try:
            server.quit()
        except Exception:
            pass

    logger.info("Bulk email send complete: %s sent, %s failed", sent_count, failed_count)
    return {"sent": sent_count, "failed": failed_count}


def send_email_with_attachment(recipient_email, subject, email_body, attachment_bytes, attachment_filename,
                                email_type="general", sent_by_user_id=None, reply_to_email=None):
    """Send HTML email with a binary file attachment (e.g. PDF receipt)."""
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = os.getenv("SMTP_PORT", "")
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if not smtp_host or not smtp_port:
        logger.error("SMTP host/port not configured.")
        log_id = _create_email_log(recipient_email, subject, email_type,
                                    sent_by_user_id, reply_to_email, email_body)
        _update_email_log(log_id, "failed", "SMTP not configured")
        return

    try:
        smtp_port = int(smtp_port)
    except ValueError:
        logger.error("SMTP_PORT must be an integer.")
        return

    log_id = _create_email_log(recipient_email, subject, email_type,
                                sent_by_user_id, reply_to_email, email_body)
    final_body = _inject_tracking_pixel(email_body, log_id)

    try:
        from_name = os.getenv("SMTP_FROM_NAME", "ECSACONM Events")
        from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username)
        msg = MIMEMultipart("mixed")
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain="ecsaconm.org")
        msg["Cc"] = ADMIN_CC_EMAIL
        msg["Reply-To"] = reply_to_email or f"{from_name} <{from_email}>"
        msg["X-Mailer"] = "ECSACONM Events Portal"
        msg.attach(MIMEText(final_body, "html", "utf-8"))

        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{attachment_filename}"')
        msg.attach(part)

        envelope_to = _cc_recipients(recipient_email)
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_username, smtp_password)
                server.sendmail(smtp_username, envelope_to, msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(smtp_username, envelope_to, msg.as_string())

        logger.info("Email with attachment sent to %s", recipient_email)
        _update_email_log(log_id, "sent")
    except Exception as e:
        logger.error("Failed to send email with attachment to %s: %s", recipient_email, str(e))
        _update_email_log(log_id, "failed", str(e))
        raise


# --- BACKGROUND TASK WRAPPER ---
def send_email_backgroundable(
    recipient_email, subject, email_body, background_tasks: BackgroundTasks = None,
    email_type="general", sent_by_user_id=None, reply_to_email=None,
):
    if background_tasks:
        background_tasks.add_task(
            send_email, recipient_email, subject, email_body,
            email_type, sent_by_user_id, reply_to_email,
        )
    else:
        send_email(recipient_email, subject, email_body,
                    email_type, sent_by_user_id, reply_to_email)


# --- EMAIL FUNCTIONS ---


def new_account_email(
    recipient_email, firstname, password, event_name=None, background_tasks: BackgroundTasks = None,
    sent_by_user_id=None,
):
    subject = "Welcome to ECSACONM Events Portal – Activate Your Account"
    try:
        template = templates.get_template("acount_creation_template.html")
        email_body = template.render(
            subject=subject,
            username=recipient_email,
            password=password,
            firstname=firstname,
            event_name=event_name,
            year=YEAR,
        )
        send_email_backgroundable(recipient_email, subject, email_body, background_tasks,
                                   email_type="new_account", sent_by_user_id=sent_by_user_id)
    except Exception as e:
        logger.error("Failed to prepare/send welcome email to %s: %s", recipient_email, str(e))


def reset_password_request_email(
    recipient_email, firstname, reset_token, background_tasks: BackgroundTasks = None
):
    subject = "Password Reset Request"
    template = templates.get_template("password_reset_request_template.html")
    email_body = template.render(
        subject=subject,
        username=recipient_email,
        firstname=firstname,
        reset_token=reset_token,
        year=YEAR,
    )
    send_email_backgroundable(recipient_email, subject, email_body, background_tasks,
                               email_type="password_reset_request")


def password_reset_email(
    recipient_email, firstname, background_tasks: BackgroundTasks = None
):
    subject = "Your ECSA-HC Event Spaces Account password has been reset"
    template = templates.get_template("password_reset_template.html")
    email_body = template.render(
        subject=subject,
        firstname=firstname,
        email=recipient_email,
        year=YEAR,
    )
    send_email_backgroundable(recipient_email, subject, email_body, background_tasks,
                               email_type="password_reset")


def account_verification_email(
    recipient_email, firstname, background_tasks: BackgroundTasks = None
):
    subject = "Your ECSA-HC Event Spaces Account has been verified"
    template = templates.get_template("account_verification_template.html")
    email_body = template.render(
        subject=subject,
        email=recipient_email,
        firstname=firstname,
        year=YEAR,
    )
    send_email_backgroundable(recipient_email, subject, email_body, background_tasks,
                               email_type="account_verification")


def account_verification_request_email(
    recipient_email,
    firstname,
    verification_token,
    background_tasks: BackgroundTasks = None,
):
    subject = "Account Verification Request"
    template = templates.get_template("account_verification_request_template.html")
    email_body = template.render(
        subject=subject,
        email=recipient_email,
        firstname=firstname,
        verification_token=verification_token,
        year=YEAR,
    )
    send_email_backgroundable(recipient_email, subject, email_body, background_tasks,
                               email_type="account_verification_request")


def organisation_verification_request_email(
    recipient_email, firstname, organisation, background_tasks: BackgroundTasks = None
):
    subject = "Organisation Verification Request"
    template = templates.get_template("organisation_verification_request_template.html")
    email_body = template.render(
        subject=subject,
        email=recipient_email,
        firstname=firstname,
        organisation=organisation.organisation,
        organisation_id=organisation.id,
        year=YEAR,
    )
    send_email_backgroundable(recipient_email, subject, email_body, background_tasks,
                               email_type="organisation_verification_request")


def organisation_approval_status_email(
    recipient_email,
    firstname,
    organisation,
    status,
    background_tasks: BackgroundTasks = None,
):
    subject = "Organisation Approval Status"
    template = templates.get_template("organisation_approval_status_template.html")
    email_body = template.render(
        subject=subject,
        email=recipient_email,
        firstname=firstname,
        organisation=organisation.organisation,
        organisation_id=organisation.id,
        status=status,
        year=YEAR,
    )
    send_email_backgroundable(recipient_email, subject, email_body, background_tasks,
                               email_type="organisation_approval_status")


def reviewer_assignment_email(
    recipient_email,
    firstname,
    password,
    abstract_title,
    event_name=None,
    background_tasks: BackgroundTasks = None,
    sent_by_user_id=None,
):
    subject = "You Have Been Assigned an Abstract to Review – ECSA Events Portal"
    template = templates.get_template("reviewer_assignment_template.html")
    email_body = template.render(
        subject=subject,
        username=recipient_email,
        firstname=firstname,
        password=password,
        abstract_title=abstract_title,
        event_name=event_name,
        year=YEAR,
    )
    send_email_backgroundable(recipient_email, subject, email_body, background_tasks,
                               email_type="reviewer_assignment", sent_by_user_id=sent_by_user_id)
