from __future__ import annotations

import hashlib
import secrets

from pydantic import BaseModel, Field

from .enums import ActionType, ResponseExpectation, SubjectRole


class ActionSubject(BaseModel):
    entity_type: str
    entity_id: str
    role: SubjectRole


def _generate_challenge_token() -> str:
    return secrets.token_hex(8)


class BrokerAction(BaseModel):
    id: str
    action_type: ActionType
    regulated: bool
    content: str | None = None
    response_expectation: ResponseExpectation
    subjects: list[ActionSubject] = []
    information_scope: dict[str, list[str]] | None = None
    challenge_token: str = Field(default_factory=_generate_challenge_token)
