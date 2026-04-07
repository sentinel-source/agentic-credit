from __future__ import annotations

from pydantic import BaseModel

from .enums import ActionType, ResponseExpectation, SubjectRole


class ActionSubject(BaseModel):
    entity_type: str
    entity_id: str
    role: SubjectRole


class BrokerAction(BaseModel):
    id: str
    action_type: ActionType
    regulated: bool
    content: str | None = None
    response_expectation: ResponseExpectation
    subjects: list[ActionSubject] = []
    information_scope: dict[str, list[str]] | None = None
