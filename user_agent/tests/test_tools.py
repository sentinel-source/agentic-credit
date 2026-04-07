import json
from unittest.mock import MagicMock

from user_agent.models import OpenCaseResponse, OperationResponse, BrokerAction
from user_agent.tools import SessionState, execute_tool


def _mock_client():
    client = MagicMock()
    return client


def test_open_case_sets_case_id():
    client = _mock_client()
    client.open_case.return_value = OpenCaseResponse(
        case_id="test-123",
        events=[],
        pending_action=BrokerAction(
            id="action-01",
            action_type="information_request",
            regulated=False,
            content="Provide your details",
            response_expectation="provide",
            challenge_token="tok-abc",
        ),
    )
    session = SessionState(user_id="user-001")
    result = execute_tool("open_case", {}, client, session)
    data = json.loads(result)
    assert data["case_id"] == "test-123"
    assert session.case_id == "test-123"
    assert session.pending_action is not None


def test_provide_sends_transcript():
    client = _mock_client()
    client.provide.return_value = OperationResponse(events=[], pending_action=None)
    session = SessionState(user_id="user-001", case_id="case-123")
    session.pending_action = {"challenge_token": "tok-xyz"}
    session.transcript.add_user("I earn 35K")

    execute_tool("provide_information", {"facts": []}, client, session)

    call_kwargs = client.provide.call_args
    assert "tok-xyz" in call_kwargs.kwargs.get("transcript", "") or "tok-xyz" in str(call_kwargs)


def test_resolve_sends_transcript():
    client = _mock_client()
    client.resolve.return_value = OperationResponse(events=[], pending_action=None)
    session = SessionState(user_id="user-001", case_id="case-123")
    session.pending_action = {"challenge_token": "tok-abc"}
    session.transcript.add_user("Yes I acknowledge")

    execute_tool("resolve_action", {
        "action_id": "action-01",
        "resolution": "acknowledged",
    }, client, session)

    call_kwargs = client.resolve.call_args
    assert "tok-abc" in str(call_kwargs)


def test_unknown_tool_returns_error():
    client = _mock_client()
    session = SessionState(user_id="user-001")
    result = execute_tool("nonexistent_tool", {}, client, session)
    data = json.loads(result)
    assert data["error"] is True


def test_no_case_returns_error():
    client = _mock_client()
    session = SessionState(user_id="user-001")  # no case_id
    result = execute_tool("provide_information", {"facts": []}, client, session)
    data = json.loads(result)
    assert data["error"] is True
    assert "No case open" in data["detail"]


def test_withdraw_marks_complete():
    client = _mock_client()
    client.withdraw.return_value = OperationResponse(events=[], pending_action=None)
    session = SessionState(user_id="user-001", case_id="case-123")
    execute_tool("withdraw", {}, client, session)
    assert session.case_complete is True
