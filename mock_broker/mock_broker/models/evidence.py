from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class EvidenceEntryResponse(BaseModel):
    timestamp: datetime
    operation: str
    data: dict[str, Any] = {}
    transcript: str | None = None
    transcript_hash: str | None = None
    challenge_token_verified: bool | None = None
    ua_version: str | None = None
    ua_version_mismatch: bool = False
