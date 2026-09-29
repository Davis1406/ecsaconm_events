"""Signed per-recipient `ref` tokens for links in outgoing emails.

A ref is "<user_id>.<sig>", where sig is a truncated HMAC of the user id
under SECRET_KEY — so an open of the tracked page can be attributed to the
person whose email the link came from, and a ref can't be forged or
incremented to impersonate someone else. It identifies only; it grants no
access to anything.
"""
import hashlib
import hmac
import os
import re
from typing import Optional
from urllib.parse import urlsplit, urlunsplit

# Links in emails that should carry the recipient's ref.
TRACKED_LINK_MARKERS = ("programme-rooms-public",)

_REF_RE = re.compile(r"^(\d{1,10})\.([0-9a-f]{12})$")


# `kind` namespaces the signature: "page-ref" tokens only ever go out in a
# recipient's own email, while "pick" tokens are handed to anyone who picks a
# name in the presentations page's searchable list — so a pick token can never
# pass as an email-link ref.
def _sig(user_id: int, kind: str = "page-ref") -> str:
    key = (os.getenv("SECRET_KEY", "") or "ecsaconm").encode()
    return hmac.new(key, f"{kind}:{int(user_id)}".encode(), hashlib.sha256).hexdigest()[:12]


def make_ref(user_id: int, kind: str = "page-ref") -> str:
    return f"{int(user_id)}.{_sig(user_id, kind)}"


def parse_ref(ref, kind: str = "page-ref") -> Optional[int]:
    """The user id a valid ref of this kind was issued for, else None."""
    m = _REF_RE.match(str(ref or "").strip())
    if not m:
        return None
    user_id = int(m.group(1))
    return user_id if hmac.compare_digest(m.group(2), _sig(user_id, kind)) else None


def with_ref(url: str, user_id) -> str:
    """Append ref=<token> (and src=email) to a tracked link. The public site
    uses hash routing, so the query lives inside the fragment
    (…/#/programme-rooms-public?event_id=1&ref=…); untracked links and
    unknown users are returned unchanged."""
    if not user_id or not any(m in (url or "") for m in TRACKED_LINK_MARKERS):
        return url
    parts = urlsplit(url)
    extra = f"ref={make_ref(user_id)}&src=email"
    if parts.fragment:
        frag = parts.fragment + ("&" if "?" in parts.fragment else "?") + extra
        return urlunsplit(parts._replace(fragment=frag))
    query = (parts.query + "&" if parts.query else "") + extra
    return urlunsplit(parts._replace(query=query))
