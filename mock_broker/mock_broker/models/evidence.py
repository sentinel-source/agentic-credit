from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class EvidenceEntryResponse(BaseModel):
    timestamp: datetime
    operation: str
    data: dict[str, Any] = {}
    transcript: str | None = None
