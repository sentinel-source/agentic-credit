"""Security utilities for URL signing and verification."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from urllib.parse import urlencode


# In production this would be loaded from configuration, not hardcoded.
_SIGNING_KEY = secrets.token_bytes(32)

# Signed tokens expire after 1 hour by default.
TOKEN_TTL_SECONDS = 3600


def sign_redirect(case_id: str, offer_id: str, destination_url: str) -> str:
    """Generate an HMAC-signed redirect token for a lender handoff URL."""
    issued_at = str(int(time.time()))
    payload = f"{case_id}:{offer_id}:{destination_url}:{issued_at}"
    signature = hmac.new(_SIGNING_KEY, payload.encode(), hashlib.sha256).hexdigest()
    return f"{signature}:{issued_at}"


def verify_redirect(
    token: str,
    case_id: str,
    offer_id: str,
    destination_url: str,
) -> tuple[bool, str]:
    """Verify an HMAC-signed redirect token. Returns (valid, reason)."""
    try:
        signature, issued_at = token.rsplit(":", 1)
    except ValueError:
        return False, "Malformed token"

    payload = f"{case_id}:{offer_id}:{destination_url}:{issued_at}"
    expected = hmac.new(_SIGNING_KEY, payload.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected):
        return False, "Invalid signature"

    try:
        issued_ts = int(issued_at)
    except ValueError:
        return False, "Invalid timestamp"

    if time.time() - issued_ts > TOKEN_TTL_SECONDS:
        return False, "Token expired"

    return True, "Valid"
