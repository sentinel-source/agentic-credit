from __future__ import annotations

from mock_broker.models.actions import BrokerAction
from mock_broker.models.enums import ActionType, CaseStatus, TERMINAL_STATUSES
from mock_broker.models.events import Event
from mock_broker.models.operations import (
    OpenCaseRequest,
    OperationResponse,
    ProvideRequest,
    ResolveActionRequest,
    SelectRequest,
)
from mock_broker.state.case import Case

from .steps import JOURNEY_STEPS, StepResult


class BlockedError(Exception):
    """Raised when an operation is blocked by a pending broker action."""

    def __init__(self, action: BrokerAction) -> None:
        self.action = action
        super().__init__(
            f"Operation blocked: pending {action.action_type.value} action "
            f"'{action.id}' must be resolved first."
        )


class TerminalError(Exception):
    """Raised when an operation is attempted on a terminal case."""

    def __init__(self, status: CaseStatus) -> None:
        self.status = status
        super().__init__(f"Case is in terminal state: {status.value}")


class JourneyEngine:
    def __init__(self) -> None:
        self._steps = JOURNEY_STEPS

    def _check_terminal(self, case: Case) -> None:
        if case.status in TERMINAL_STATUSES:
            raise TerminalError(case.status)

    def _check_blocked(self, case: Case, *, allow_provide: bool = False) -> None:
        if case.pending_action is None:
            return
        if allow_provide and case.pending_action.action_type == ActionType.information_request:
            return
        raise BlockedError(case.pending_action)

    def _apply(self, case: Case, result: StepResult) -> OperationResponse:
        case.stage = result.advance_to
        case.pending_action = result.pending_action
        if result.status is not None:
            case.status = result.status
        case.event_log.extend(result.events)
        return OperationResponse(
            events=result.events,
            pending_action=result.pending_action,
        )

    def process_open(self, case: Case, request: OpenCaseRequest) -> OperationResponse:
        step_fn = self._steps.get(("open", case.stage))
        if step_fn is None:
            raise ValueError(f"No step defined for open at stage {case.stage}")
        result = step_fn(case, request)
        # Merge initial data into profile
        case.profile.facts.extend(request.facts)
        case.profile.attributes.extend(request.attributes)
        case.goals.extend(request.goals)
        case.record_evidence("open_case", {
            "facts": [f.model_dump() for f in request.facts],
            "attributes": [a.model_dump() for a in request.attributes],
            "goals": [g.model_dump() for g in request.goals],
        })
        return self._apply(case, result)

    def process_provide(self, case: Case, request: ProvideRequest) -> OperationResponse:
        self._check_terminal(case)
        self._check_blocked(case, allow_provide=True)
        step_fn = self._steps.get(("provide", case.stage))
        if step_fn is None:
            raise ValueError(f"No step defined for provide at stage {case.stage}")
        # Merge provided data
        case.profile.facts.extend(request.facts)
        case.profile.attributes.extend(request.attributes)
        case.goals.extend(request.goals)
        result = step_fn(case, request)
        case.record_evidence("provide", {
            "facts": [f.model_dump() for f in request.facts],
            "attributes": [a.model_dump() for a in request.attributes],
            "goals": [g.model_dump() for g in request.goals],
        }, transcript=request.transcript)
        return self._apply(case, result)

    def process_select(self, case: Case, request: SelectRequest) -> OperationResponse:
        self._check_terminal(case)
        self._check_blocked(case)
        step_fn = self._steps.get(("select", case.stage))
        if step_fn is None:
            raise ValueError(f"No step defined for select at stage {case.stage}")
        result = step_fn(case, request)
        case.record_evidence("select", {
            "entity_type": request.entity_type,
            "entity_id": request.entity_id,
        })
        return self._apply(case, result)

    def process_resolve(self, case: Case, request: ResolveActionRequest) -> OperationResponse:
        self._check_terminal(case)
        if case.pending_action is None:
            raise ValueError("No pending action to resolve")
        if case.pending_action.id != request.action_id:
            raise ValueError(
                f"Action ID mismatch: expected '{case.pending_action.id}', "
                f"got '{request.action_id}'"
            )
        step_fn = self._steps.get(("resolve", case.stage))
        if step_fn is None:
            raise ValueError(f"No step defined for resolve at stage {case.stage}")
        result = step_fn(case, request)
        case.record_evidence("resolve_action", {
            "action_id": request.action_id,
            "resolution": request.resolution.value,
        }, transcript=request.transcript)
        return self._apply(case, result)

    def process_withdraw(self, case: Case) -> OperationResponse:
        self._check_terminal(case)
        step_fn = self._steps.get(("withdraw", None))
        if step_fn is None:
            raise ValueError("No withdraw step defined")
        result = step_fn(case, None)
        case.record_evidence("withdraw")
        return self._apply(case, result)
