"""
Download Google Drive proof-of-payment and badge photo files for all participants,
save them locally, and update the database paths.

SETUP (one time):
  1. Go to https://console.cloud.google.com/
  2. Create a project → Enable "Google Drive API"
  3. Go to APIs & Services → Credentials → Create Credentials → OAuth client ID
     Application type: Desktop app  →  Download JSON  →  save as credentials.json
     in the same folder as this script (api/scripts/credentials.json)
  4. Run:  python scripts/download_drive_files.py
     A browser window will open for Google sign-in (use the account that owns the Form/Drive).
     The token is cached in api/scripts/token.json for future runs.
"""

import os, re, sys, io, hashlib, mimetypes, pickle, json, time
from datetime import datetime
from pathlib import Path

# ── ensure we can import app modules ──────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

import mysql.connector
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ── config ─────────────────────────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SCRIPT_DIR   = Path(__file__).parent
CREDS_FILE   = SCRIPT_DIR / "credentials.json"
TOKEN_FILE   = SCRIPT_DIR / "token.json"
API_DIR      = SCRIPT_DIR.parent
PROOF_DIR    = API_DIR / "uploads" / "payment_receipts"
PHOTO_BASE   = API_DIR / "uploads" / "picture" / "profile_picture"

DB_CONFIG = dict(
    host="127.0.0.1", user="root", password="root", database="ecsaconm_events"
)

# ── helpers ────────────────────────────────────────────────────────────────────

def get_drive_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_FILE.exists():
                print(f"\n✗  credentials.json not found at {CREDS_FILE}")
                print("   See setup instructions at the top of this script.\n")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
        print(f"✓  Token saved to {TOKEN_FILE}")
    return build("drive", "v3", credentials=creds)


def extract_file_id(url: str):
    """Extract Google Drive file ID from open/view/uc links."""
    m = re.search(r"[?&/]id=([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    return None


def download_file(service, file_id: str) -> tuple[bytes, str]:
    """Download a Drive file, return (content_bytes, mime_type)."""
    meta = service.files().get(fileId=file_id, fields="name,mimeType").execute()
    mime = meta.get("mimeType", "application/octet-stream")
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request, chunksize=4 * 1024 * 1024)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue(), mime


def mime_to_ext(mime: str, fallback="bin") -> str:
    ext = mimetypes.guess_extension(mime)
    if ext:
        return ext.lstrip(".")
    mapping = {
        "image/jpeg": "jpg", "image/png": "png", "image/gif": "gif",
        "image/webp": "webp", "application/pdf": "pdf",
    }
    return mapping.get(mime, fallback)


def short_uid(seed: str) -> str:
    return hashlib.md5(seed.encode()).hexdigest()[:8]


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n── Google Drive File Downloader ─────────────────────────────")
    service = get_drive_service()

    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()

    proof_ok = proof_fail = 0
    photo_ok = photo_fail = 0

    # ── 1. PROOF OF PAYMENT ───────────────────────────────────────────────────
    print("\n[1/2] Downloading proof-of-payment files …")
    cur.execute("""
        SELECT r.id, r.user_id, r.payment_proof
        FROM   registration r
        WHERE  r.payment_proof LIKE '%drive.google%'
    """)
    proof_rows = cur.fetchall()
    print(f"      Found {len(proof_rows)} registration(s) with Drive proof URLs")

    for reg_id, user_id, url in proof_rows:
        file_id = extract_file_id(url)
        if not file_id:
            print(f"  ✗  reg {reg_id}: cannot parse file ID from {url}")
            proof_fail += 1
            continue
        try:
            data, mime = download_file(service, file_id)
            ext = mime_to_ext(mime, "pdf")
            fname = f"proof_{reg_id}_{short_uid(str(reg_id))}.{ext}"
            PROOF_DIR.mkdir(parents=True, exist_ok=True)
            dest = PROOF_DIR / fname
            dest.write_bytes(data)
            local_path = f"uploads/payment_receipts/{fname}"
            cur.execute(
                "UPDATE registration SET payment_proof=%s WHERE id=%s",
                (local_path, reg_id)
            )
            conn.commit()
            print(f"  ✓  reg {reg_id} → {local_path}  ({len(data)//1024} KB)")
            proof_ok += 1
        except Exception as e:
            print(f"  ✗  reg {reg_id}: {e}")
            proof_fail += 1
        time.sleep(0.3)   # be gentle with the API

    # ── 2. BADGE / PASSPORT PHOTOS ────────────────────────────────────────────
    print(f"\n[2/2] Downloading badge photos …")
    cur.execute("""
        SELECT p.id, p.user_id, p.path
        FROM   user_photo p
        WHERE  p.path LIKE '%drive.google%'
          AND  p.deleted_at IS NULL
    """)
    photo_rows = cur.fetchall()
    print(f"      Found {len(photo_rows)} photo record(s) with Drive URLs")

    for photo_id, user_id, url in photo_rows:
        file_id = extract_file_id(url)
        if not file_id:
            print(f"  ✗  photo {photo_id}: cannot parse file ID from {url}")
            photo_fail += 1
            continue
        try:
            data, mime = download_file(service, file_id)
            ext = mime_to_ext(mime, "jpg")
            ts  = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            uid = short_uid(f"{user_id}_{ts}")
            folder_name = f"{user_id}_{ts}_{uid}"
            dest_dir = PHOTO_BASE / folder_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / f"profile.{ext}"
            dest.write_bytes(data)
            local_path = f"uploads/picture/profile_picture/{folder_name}/profile.{ext}"
            cur.execute(
                "UPDATE user_photo SET path=%s WHERE id=%s",
                (local_path, photo_id)
            )
            conn.commit()
            print(f"  ✓  user {user_id} → {local_path}  ({len(data)//1024} KB)")
            photo_ok += 1
        except Exception as e:
            print(f"  ✗  photo {photo_id}: {e}")
            photo_fail += 1
        time.sleep(0.3)

    # ── summary ───────────────────────────────────────────────────────────────
    print(f"""
── Summary ──────────────────────────────────────────────
  Proof of payment:  {proof_ok} downloaded,  {proof_fail} failed
  Badge photos:      {photo_ok} downloaded,  {photo_fail} failed
─────────────────────────────────────────────────────────
""")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
