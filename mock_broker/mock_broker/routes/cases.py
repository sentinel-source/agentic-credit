from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from mock_broker.journey.engine import BlockedError, JourneyEngine, TerminalError
from mock_broker.models.evidence import EvidenceEntryResponse
from mock_broker.models.operations import (
    CaseState,
    OpenCaseRequest,
    OpenCaseResponse,
    OperationResponse,
    ProvideRequest,
    ResolveActionRequest,
    SelectRequest,
)
from mock_broker.state.case_store import CaseStore

router = APIRouter()


def _get_store(request: Request) -> CaseStore:
    return request.app.state.store


def _get_engine(request: Request) -> JourneyEngine:
    return request.app.state.engine


def _get_case(request: Request, case_id: str):
    case = _get_store(request).get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    return case


@router.post("", status_code=201, response_model=OpenCaseResponse)
def open_case(request: Request, body: OpenCaseRequest | None = None):
    body = body or OpenCaseRequest()
    store = _get_store(request)
    engine = _get_engine(request)
    case = store.create()
    try:
        response = engine.process_open(case, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return OpenCaseResponse(
        case_id=case.case_id,
        events=response.events,
        pending_action=response.pending_action,
    )


@router.post("/{case_id}/provide", response_model=OperationResponse)
def provide(request: Request, case_id: str, body: ProvideRequest):
    case = _get_case(request, case_id)
    engine = _get_engine(request)
    try:
        return engine.process_provide(case, body)
    except TerminalError:
        raise HTTPException(status_code=409, detail=f"Case is in terminal state: {case.status.value}")
    except BlockedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{case_id}/state", response_model=CaseState)
def get_state(request: Request, case_id: str):
    case = _get_case(request, case_id)
    return CaseState(
        case_id=case.case_id,
        status=case.status,
        profile=case.profile,
        goals=case.goals,
        plans=case.plans,
        offers=case.offers,
        pending_action=case.pending_action,
        evidence=[
            EvidenceEntryResponse(
                timestamp=e.timestamp,
                operation=e.operation,
                data=e.data,
                transcript=e.transcript,
            )
            for e in case.evidence_log
        ],
    )


@router.post("/{case_id}/select", response_model=OperationResponse)
def select(request: Request, case_id: str, body: SelectRequest):
    case = _get_case(request, case_id)
    engine = _get_engine(request)
    try:
        return engine.process_select(case, body)
    except TerminalError:
        raise HTTPException(status_code=409, detail=f"Case is in terminal state: {case.status.value}")
    except BlockedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{case_id}/resolve", response_model=OperationResponse)
def resolve_action(request: Request, case_id: str, body: ResolveActionRequest):
    case = _get_case(request, case_id)
    engine = _get_engine(request)
    try:
        return engine.process_resolve(case, body)
    except TerminalError:
        raise HTTPException(status_code=409, detail=f"Case is in terminal state: {case.status.value}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{case_id}/withdraw", response_model=OperationResponse)
def withdraw(request: Request, case_id: str):
    case = _get_case(request, case_id)
    engine = _get_engine(request)
    try:
        return engine.process_withdraw(case)
    except TerminalError:
        raise HTTPException(status_code=409, detail=f"Case is in terminal state: {case.status.value}")
