import os
import smtplib
import logging
import time
import uuid
from collections import deque
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
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

# Public frontend origin used to build clickable links inside emails, e.g.
# "https://events.ecsaconm.org" in production.
CLIENT_ORIGIN = os.getenv("CLIENT_ORIGIN", "https://events.ecsaconm.org")

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


def _reset_email_log_for_resend(log_id):
    """Reset an existing (failed) EmailLog row to 'pending' ahead of a resend
    attempt, so a successful resend updates that same row in place instead of
    leaving a stale 'failed' entry sitting alongside a new 'sent' one."""
    try:
        from core.database import SessionLocal
        from models.models import EmailLog
        db = SessionLocal()
        try:
            record = db.query(EmailLog).filter(EmailLog.id == log_id).first()
            if record:
                record.status = "pending"
                record.error_message = None
                record.sent_at = datetime.utcnow()
                record.opened_at = None
                record.opened_count = 0
                db.commit()
        finally:
            db.close()
    except Exception as log_err:
        logger.error("Failed to reset email log %s for resend: %s", log_id, log_err)


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


def _build_image_invitation_message(from_name, from_email, recipient_email, subject, reply_to_email,
                                     image_bytes, image_filename, image_subtype, final_body_html):
    """A message whose body is nothing but the given image — embedded inline
    (via a cid: reference, so it renders directly in the email body) and
    attached again as a separate downloadable file, per the same bytes."""
    outer = MIMEMultipart("mixed")
    outer["From"] = f"{from_name} <{from_email}>"
    outer["To"] = recipient_email
    outer["Cc"] = ADMIN_CC_EMAIL
    outer["Subject"] = subject
    outer["Date"] = formatdate(localtime=True)
    outer["Message-ID"] = make_msgid(domain="ecsaconm.org")
    outer["Reply-To"] = reply_to_email or f"{from_name} <{from_email}>"
    outer["X-Mailer"] = "ECSACONM Events Portal"

    related = MIMEMultipart("related")
    related.attach(MIMEText(final_body_html, "html", "utf-8"))
    inline_img = MIMEImage(image_bytes, _subtype=image_subtype)
    inline_img.add_header("Content-ID", "<gala_invite_image>")
    inline_img.add_header("Content-Disposition", "inline", filename=image_filename)
    related.attach(inline_img)
    outer.attach(related)

    attach_img = MIMEImage(image_bytes, _subtype=image_subtype)
    attach_img.add_header("Content-Disposition", "attachment", filename=image_filename)
    outer.attach(attach_img)
    return outer


def _image_invitation_body_html(cid="gala_invite_image"):
    """The entire email body: just the inline image, no other words."""
    return (
        '<!DOCTYPE html><html><body style="margin:0;padding:0;">'
        f'<img src="cid:{cid}" alt="Invitation" style="display:block;width:100%;max-width:650px;margin:0 auto;" />'
        '</body></html>'
    )


def send_image_invitation_email(recipient_email, subject, image_bytes, image_filename, image_subtype="jpeg",
                                 email_type="general", sent_by_user_id=None, reply_to_email=None):
    """Send a one-off email whose entire body is the given image — embedded
    inline in the HTML and attached again as a file. Used for trial sends."""
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = os.getenv("SMTP_PORT", "")
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if not smtp_host or not smtp_port:
        logger.error("SMTP host/port not configured.")
        log_id = _create_email_log(recipient_email, subject, email_type,
                                    sent_by_user_id, reply_to_email, "[image invitation]")
        _update_email_log(log_id, "failed", "SMTP not configured")
        return

    try:
        smtp_port = int(smtp_port)
    except ValueError:
        logger.error("SMTP_PORT must be an integer.")
        return

    log_id = _create_email_log(recipient_email, subject, email_type,
                                sent_by_user_id, reply_to_email, "[image invitation]")
    final_body = _inject_tracking_pixel(_image_invitation_body_html(), log_id)

    try:
        from_name = os.getenv("SMTP_FROM_NAME", "ECSACONM Events")
        from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username)
        message = _build_image_invitation_message(
            from_name, from_email, recipient_email, subject, reply_to_email,
            image_bytes, image_filename, image_subtype, final_body,
        )

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

        logger.info("Image invitation email sent to %s", recipient_email)
        _update_email_log(log_id, "sent")
    except Exception as e:
        logger.error("Failed to send image invitation to %s: %s", recipient_email, str(e))
        _update_email_log(log_id, "failed", str(e))
        raise


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


def _load_recent_send_times(window_seconds=3600):
    """Epoch-second timestamps of emails successfully sent within the last
    `window_seconds`, read from EmailLog. Seeds the rolling-hour quota counter
    in send_bulk_emails() so a bulk send also accounts for mail already sent by
    other requests (e.g. account/profile emails) in the same window."""
    from datetime import datetime, timedelta
    import calendar
    from core.database import SessionLocal
    from models.models import EmailLog

    cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
    db = SessionLocal()
    try:
        rows = (
            db.query(EmailLog.sent_at)
            .filter(EmailLog.status == "sent", EmailLog.sent_at >= cutoff)
            .all()
        )
        times = []
        for r in rows:
            dt = r[0]
            if dt is None:
                continue
            # Naive DB timestamps are UTC (server default func.now()); treat
            # them as such regardless of the process timezone.
            times.append(calendar.timegm(dt.timetuple()) if dt.tzinfo is None else dt.timestamp())
        return times
    finally:
        db.close()


def send_bulk_emails(jobs, delay_seconds=0.3, attachment_bytes=None, attachment_filename=None,
                      inline_image_bytes=None, inline_image_filename=None, inline_image_subtype="jpeg"):
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

    `attachment_bytes`/`attachment_filename`, if given, are attached to every
    message in the batch (e.g. the same invitation HTML embedded in the body
    also handed over as a downloadable/keepsake file).

    `inline_image_bytes`/`inline_image_filename`/`inline_image_subtype`, if
    given, take over the whole message body for every job in the batch: the
    body becomes just that image, embedded inline and attached again as a
    file (job["email_body"] is ignored in that case).

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

    def _open_connection():
        if smtp_port == 465:
            conn = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
        else:
            conn = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            conn.starttls()
        conn.login(smtp_username, smtp_password)
        return conn

    try:
        server = _open_connection()
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
    msgs_on_connection = 0
    # Mail servers commonly cap how many messages one SMTP session may send
    # (Exim/cPanel default is often ~25-100) and reply "421 too many
    # messages in this connection", tearing the socket down. Rotate to a
    # fresh, re-authenticated connection before that happens.
    max_msgs_per_connection = int(os.getenv("SMTP_MAX_MSGS_PER_CONNECTION", "20"))

    # ── Rolling-hour quota pacing ─────────────────────────────────────────
    # The mail host enforces a domain-wide hourly cap (e.g. Exim/cPanel's
    # "max emails per hour", 500/hr here). A large bulk send can blow straight
    # through it, after which the server starts refusing connections and
    # replying "550 … exceeded the max emails per hour" — and those messages
    # are lost. Track sends in a rolling 60-minute window (seeded from
    # EmailLog so mail sent elsewhere counts too) and pause until a slot frees
    # up rather than overrunning the cap.
    try:
        # Default 450 leaves headroom below the host's 500/hr domain limit for
        # mail this app didn't send (other mailboxes on the domain, etc.).
        max_per_hour = int(os.getenv("SMTP_MAX_EMAILS_PER_HOUR", "450"))
    except ValueError:
        max_per_hour = 450
    quota_window = 3600
    try:
        send_times = deque(_load_recent_send_times(quota_window))
    except Exception as e:
        logger.warning("Could not load recent send times for quota pacing: %s", e)
        send_times = deque()

    def _await_quota_slot():
        """Block until the rolling-hour send count is below the cap."""
        if max_per_hour <= 0:
            return
        now = time.time()
        while send_times and now - send_times[0] >= quota_window:
            send_times.popleft()
        while len(send_times) >= max_per_hour:
            wait = quota_window - (now - send_times[0]) + 2
            logger.info(
                "Hourly email quota reached (%d/%d) — pausing %.0fs before continuing",
                len(send_times), max_per_hour, wait,
            )
            time.sleep(max(1, wait))
            now = time.time()
            while send_times and now - send_times[0] >= quota_window:
                send_times.popleft()

    # Circuit breaker: if the mail host starts actively refusing connections
    # (e.g. after an hourly-quota rejection triggers anti-abuse blocking),
    # retrying immediately for every remaining job in the batch just burns
    # through the whole list in seconds, marking everyone "failed" instead
    # of genuinely attempting them — worse, it hammers a server that's
    # already refusing us, risking a longer/harsher block. After a few
    # consecutive reconnect failures, stop processing the rest of the batch
    # entirely and leave those jobs unattempted (not "failed") so a later
    # retry (e.g. the missing-recipients recovery flow) picks them up
    # cleanly instead of needing to distinguish "really tried and failed"
    # from "gave up early".
    consecutive_reconnect_failures = 0
    max_consecutive_reconnect_failures = 3
    circuit_open = False

    try:
        for i, job in enumerate(jobs):
            if circuit_open:
                break
            # Respect the rolling-hour quota before doing any work for this job.
            _await_quota_slot()

            recipient_email = job["recipient_email"]
            subject = job["subject"]
            email_body = job["email_body"]
            email_type = job.get("email_type", "general")
            sent_by_user_id = job.get("sent_by_user_id")
            reply_to_email = job.get("reply_to_email")

            existing_log_id = job.get("existing_log_id")
            if existing_log_id:
                _reset_email_log_for_resend(existing_log_id)
                log_id = existing_log_id
            else:
                log_id = _create_email_log(recipient_email, subject, email_type,
                                            sent_by_user_id, reply_to_email, email_body)
            if inline_image_bytes:
                final_body = _inject_tracking_pixel(_image_invitation_body_html(), log_id)
                message = _build_image_invitation_message(
                    from_name, from_email, recipient_email, subject, reply_to_email,
                    inline_image_bytes, inline_image_filename, inline_image_subtype, final_body,
                )
                if msgs_on_connection >= max_msgs_per_connection:
                    try:
                        server.quit()
                    except Exception:
                        pass
                    server = _open_connection()
                    msgs_on_connection = 0
                envelope_to = _cc_recipients(recipient_email)
                try:
                    server.sendmail(smtp_username, envelope_to, message.as_string())
                    msgs_on_connection += 1
                    logger.info("Email sent successfully to %s", recipient_email)
                    _update_email_log(log_id, "sent")
                    sent_count += 1
                    send_times.append(time.time())
                    consecutive_reconnect_failures = 0
                except (smtplib.SMTPServerDisconnected, smtplib.SMTPResponseException, OSError) as e:
                    logger.warning("SMTP connection dropped sending to %s (%s) - pausing then reconnecting and retrying once",
                                    recipient_email, e)
                    time.sleep(5)
                    try:
                        server = _open_connection()
                        msgs_on_connection = 0
                        server.sendmail(smtp_username, envelope_to, message.as_string())
                        msgs_on_connection += 1
                        logger.info("Email sent successfully to %s (after reconnect)", recipient_email)
                        _update_email_log(log_id, "sent")
                        sent_count += 1
                        send_times.append(time.time())
                        consecutive_reconnect_failures = 0
                    except Exception as e2:
                        logger.error("Failed to send email to %s after reconnect: %s", recipient_email, str(e2))
                        _update_email_log(log_id, "failed", str(e2))
                        failed_count += 1
                        consecutive_reconnect_failures += 1
                        if consecutive_reconnect_failures >= max_consecutive_reconnect_failures:
                            logger.error(
                                "Mail host unreachable after %d consecutive reconnect failures — "
                                "stopping this batch early (%d of %d jobs left unattempted, not marked failed).",
                                consecutive_reconnect_failures, len(jobs) - i - 1, len(jobs),
                            )
                            circuit_open = True
                            break
                except Exception as e:
                    logger.error("Failed to send email to %s: %s", recipient_email, str(e))
                    _update_email_log(log_id, "failed", str(e))
                    failed_count += 1
                if delay_seconds and i < len(jobs) - 1:
                    time.sleep(delay_seconds)
                continue

            final_body = _inject_tracking_pixel(email_body, log_id)

            message = MIMEMultipart("mixed") if attachment_bytes else MIMEMultipart("alternative")
            message["From"] = f"{from_name} <{from_email}>"
            message["To"] = recipient_email
            message["Cc"] = ADMIN_CC_EMAIL
            message["Subject"] = subject
            message["Date"] = formatdate(localtime=True)
            message["Message-ID"] = make_msgid(domain="ecsaconm.org")
            message["Reply-To"] = reply_to_email or f"{from_name} <{from_email}>"
            message["X-Mailer"] = "ECSACONM Events Portal"
            if attachment_bytes:
                alt_part = MIMEMultipart("alternative")
                alt_part.attach(MIMEText(final_body, "html", "utf-8"))
                message.attach(alt_part)
                file_part = MIMEBase("application", "octet-stream")
                file_part.set_payload(attachment_bytes)
                encoders.encode_base64(file_part)
                file_part.add_header(
                    "Content-Disposition", f'attachment; filename="{attachment_filename or "attachment"}"'
                )
                message.attach(file_part)
            else:
                message.attach(MIMEText(final_body, "html", "utf-8"))
            envelope_to = _cc_recipients(recipient_email)

            if msgs_on_connection >= max_msgs_per_connection:
                try:
                    server.quit()
                except Exception:
                    pass
                server = _open_connection()
                msgs_on_connection = 0

            try:
                server.sendmail(smtp_username, envelope_to, message.as_string())
                msgs_on_connection += 1
                logger.info("Email sent successfully to %s", recipient_email)
                _update_email_log(log_id, "sent")
                sent_count += 1
                send_times.append(time.time())
                consecutive_reconnect_failures = 0
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPResponseException, OSError) as e:
                # The server dropped/refused the connection mid-batch (the
                # same per-connection cap, or a transient network blip) —
                # pause briefly, then reconnect once and retry this one
                # message before giving up.
                logger.warning("SMTP connection dropped sending to %s (%s) - pausing then reconnecting and retrying once",
                                recipient_email, e)
                time.sleep(5)
                try:
                    server = _open_connection()
                    msgs_on_connection = 0
                    server.sendmail(smtp_username, envelope_to, message.as_string())
                    msgs_on_connection += 1
                    logger.info("Email sent successfully to %s (after reconnect)", recipient_email)
                    _update_email_log(log_id, "sent")
                    sent_count += 1
                    send_times.append(time.time())
                    consecutive_reconnect_failures = 0
                except Exception as e2:
                    logger.error("Failed to send email to %s after reconnect: %s", recipient_email, str(e2))
                    _update_email_log(log_id, "failed", str(e2))
                    failed_count += 1
                    consecutive_reconnect_failures += 1
                    if consecutive_reconnect_failures >= max_consecutive_reconnect_failures:
                        logger.error(
                            "Mail host unreachable after %d consecutive reconnect failures — "
                            "stopping this batch early (%d of %d jobs left unattempted, not marked failed).",
                            consecutive_reconnect_failures, len(jobs) - i - 1, len(jobs),
                        )
                        circuit_open = True
                        break
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

    # logger.warning (not .info) so this summary is visible even if INFO-level
    # logging is filtered out at the deployment's logging config/handler —
    # this final tally matters operationally regardless of log verbosity.
    logger.warning(
        "Bulk email send complete: %s sent, %s failed, %s left unattempted (circuit breaker%s)",
        sent_count, failed_count, len(jobs) - sent_count - failed_count,
        " tripped" if circuit_open else " not tripped",
    )
    return {"sent": sent_count, "failed": failed_count, "circuit_open": circuit_open}


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
    reset_link = f"{CLIENT_ORIGIN}/#/reset-password/{reset_token}"
    template = templates.get_template("password_reset_request_template.html")
    email_body = template.render(
        subject=subject,
        username=recipient_email,
        firstname=firstname,
        reset_token=reset_token,
        reset_link=reset_link,
        year=YEAR,
    )
    send_email_backgroundable(recipient_email, subject, email_body, background_tasks,
                               email_type="password_reset_request")


def password_reset_email(
    recipient_email, firstname, background_tasks: BackgroundTasks = None
):
    subject = "Your ECSACONM Events Portal password has been reset"
    template = templates.get_template("password_reset_template.html")
    email_body = template.render(
        subject=subject,
        firstname=firstname,
        email=recipient_email,
        year=YEAR,
    )
    send_email_backgroundable(recipient_email, subject, email_body, background_tasks,
                               email_type="password_reset")


def admin_password_reset_email(
    recipient_email, firstname, new_password, background_tasks: BackgroundTasks = None,
    sent_by_user_id=None,
):
    """Sent when an admin sets a user's password directly (random or
    admin-typed) via the Users admin section — unlike password_reset_email
    above, this carries the actual new password since the user didn't
    request or choose it themselves."""
    subject = "Your ECSACONM Events Portal password has been reset by an administrator"
    template = templates.get_template("admin_password_reset_template.html")
    email_body = template.render(
        subject=subject,
        firstname=firstname,
        email=recipient_email,
        password=new_password,
        year=YEAR,
    )
    send_email_backgroundable(recipient_email, subject, email_body, background_tasks,
                               email_type="admin_password_reset", sent_by_user_id=sent_by_user_id)


def account_verification_email(
    recipient_email, firstname, background_tasks: BackgroundTasks = None
):
    subject = "Your ECSACONM Events Portal account has been verified"
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
    subject = "You Have Been Assigned an Abstract to Review – ECSACONM Events Portal"
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
