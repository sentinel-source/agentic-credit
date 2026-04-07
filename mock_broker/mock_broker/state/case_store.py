from __future__ import annotations

import uuid

from mock_broker.models.enums import TERMINAL_STATUSES

from .case import Case


class DuplicateUserError(Exception):
    """Raised when a user already has an open case."""

    def __init__(self, user_id: str, existing_case_id: str) -> None:
        self.user_id = user_id
        self.existing_case_id = existing_case_id
        super().__init__(
            f"User '{user_id}' already has an open case: '{existing_case_id}'. "
            "Resolve or withdraw the existing case before opening a new one."
        )


class CaseStore:
    def __init__(self) -> None:
        self._cases: dict[str, Case] = {}

    def create(self, user_id: str) -> Case:
        # Check for existing open case for this user
        for case in self._cases.values():
            if case.user_id == user_id and case.status not in TERMINAL_STATUSES:
                raise DuplicateUserError(user_id, case.case_id)
        case_id = uuid.uuid4().hex[:12]
        case = Case(case_id=case_id, user_id=user_id)
        self._cases[case_id] = case
        return case

    def get(self, case_id: str) -> Case | None:
        return self._cases.get(case_id)
