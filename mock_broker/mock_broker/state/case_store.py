from __future__ import annotations

import uuid

from .case import Case


class CaseStore:
    def __init__(self) -> None:
        self._cases: dict[str, Case] = {}

    def create(self) -> Case:
        case_id = uuid.uuid4().hex[:12]
        case = Case(case_id=case_id)
        self._cases[case_id] = case
        return case

    def get(self, case_id: str) -> Case | None:
        return self._cases.get(case_id)
