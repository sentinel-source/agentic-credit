"""HTTP client for the Credit Broker API."""

from __future__ import annotations

import httpx

from .models import (
    AttributeTypeDefinition,
    CaseState,
    FactTypeDefinition,
    GoalTypeDefinition,
    OpenCaseResponse,
    OperationResponse,
)

UA_VERSION = "user-agent/0.1.0"


class BrokerClient:
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=30.0,
            headers={"X-UA-Version": UA_VERSION},
        )

    def close(self) -> None:
        self._client.close()

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.status_code >= 400:
            detail = resp.json().get("detail", resp.text)
            raise BrokerError(resp.status_code, detail)

    # --- Vocabulary ---

    def load_fact_types(self) -> list[FactTypeDefinition]:
        resp = self._client.get("/vocabulary/fact-types")
        self._raise_for_status(resp)
        return [FactTypeDefinition(**item) for item in resp.json()]

    def load_attribute_types(self) -> list[AttributeTypeDefinition]:
        resp = self._client.get("/vocabulary/attribute-types")
        self._raise_for_status(resp)
        return [AttributeTypeDefinition(**item) for item in resp.json()]

    def load_goal_types(self) -> list[GoalTypeDefinition]:
        resp = self._client.get("/vocabulary/goal-types")
        self._raise_for_status(resp)
        return [GoalTypeDefinition(**item) for item in resp.json()]

    def load_vocabulary(self) -> dict:
        return {
            "fact_types": self.load_fact_types(),
            "attribute_types": self.load_attribute_types(),
            "goal_types": self.load_goal_types(),
        }

    # --- Protocol operations ---

    def open_case(self, user_id: str, **kwargs) -> OpenCaseResponse:
        body = {"user_id": user_id, **kwargs}
        resp = self._client.post("/cases", json=body)
        self._raise_for_status(resp)
        return OpenCaseResponse(**resp.json())

    def provide(
        self,
        case_id: str,
        facts: list[dict] | None = None,
        attributes: list[dict] | None = None,
        goals: list[dict] | None = None,
        transcript: str | None = None,
    ) -> OperationResponse:
        body: dict = {
            "facts": facts or [],
            "attributes": attributes or [],
            "goals": goals or [],
        }
        if transcript is not None:
            body["transcript"] = transcript
        resp = self._client.post(f"/cases/{case_id}/provide", json=body)
        self._raise_for_status(resp)
        return OperationResponse(**resp.json())

    def get_state(self, case_id: str) -> CaseState:
        resp = self._client.get(f"/cases/{case_id}/state")
        self._raise_for_status(resp)
        return CaseState(**resp.json())

    def select(
        self,
        case_id: str,
        entity_type: str,
        entity_id: str,
        transcript: str | None = None,
    ) -> OperationResponse:
        body: dict = {"entity_type": entity_type, "entity_id": entity_id}
        if transcript is not None:
            body["transcript"] = transcript
        resp = self._client.post(f"/cases/{case_id}/select", json=body)
        self._raise_for_status(resp)
        return OperationResponse(**resp.json())

    def resolve(
        self,
        case_id: str,
        action_id: str,
        resolution: str,
        transcript: str | None = None,
    ) -> OperationResponse:
        body: dict = {"action_id": action_id, "resolution": resolution}
        if transcript is not None:
            body["transcript"] = transcript
        resp = self._client.post(f"/cases/{case_id}/resolve", json=body)
        self._raise_for_status(resp)
        return OperationResponse(**resp.json())

    def withdraw(self, case_id: str) -> OperationResponse:
        resp = self._client.post(f"/cases/{case_id}/withdraw")
        self._raise_for_status(resp)
        return OperationResponse(**resp.json())


class BrokerError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Broker error {status_code}: {detail}")
