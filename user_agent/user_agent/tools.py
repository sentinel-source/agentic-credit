"""Claude tool definitions and dispatch for broker operations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .client import BrokerClient, BrokerError
from .transcript import TranscriptAccumulator


@dataclass
class SessionState:
    """Tracks the current session state across tool calls."""

    case_id: str | None = None
    user_id: str = ""
    pending_action: dict[str, Any] | None = None
    transcript: TranscriptAccumulator = field(default_factory=TranscriptAccumulator)
    case_complete: bool = False


TOOL_DEFINITIONS = [
    {
        "name": "open_case",
        "description": (
            "Open a new credit broking case with the broker. Call this when the "
            "user first indicates they want a loan or financial product. Uses the "
            "configured user_id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "provide_information",
        "description": (
            "Submit financial facts, party attributes, and/or goals to the broker. "
            "Use this to send the user's information after translating it into "
            "structured data using the broker's vocabulary. You may call this "
            "multiple times as you gather more information. Include a transcript "
            "of the relevant conversation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "facts": {
                    "type": "array",
                    "description": "Financial facts structured per the broker's fact type vocabulary.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Unique ID for this fact (e.g. 'f1', 'f2')"},
                            "fact_type": {"type": "string", "description": "Fact type name from the vocabulary"},
                            "value": {
                                "type": "object",
                                "properties": {
                                    "operator": {
                                        "type": "string",
                                        "enum": ["eq", "gte", "lte", "approx", "between"],
                                        "description": "Value operator. Use 'eq' for exact, 'approx' for estimates.",
                                    },
                                    "value": {"description": "The value (number, string, or boolean)"},
                                },
                                "required": ["operator", "value"],
                            },
                        },
                        "required": ["id", "fact_type", "value"],
                    },
                },
                "attributes": {
                    "type": "array",
                    "description": "Party attributes (name, DOB, address, etc.).",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "attribute_type": {"type": "string"},
                            "value": {"description": "The attribute value"},
                        },
                        "required": ["id", "attribute_type", "value"],
                    },
                },
                "goals": {
                    "type": "array",
                    "description": "Financial goals from the broker's goal type vocabulary.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "goal_type": {"type": "string", "description": "Goal type name from the vocabulary"},
                            "statement": {"type": "string", "description": "Natural language description of the goal"},
                        },
                        "required": ["id", "goal_type"],
                    },
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_state",
        "description": (
            "Query the current case state from the broker. Returns the full "
            "profile, goals, plans, offers, and any pending action. Use this "
            "when you need to check what's available or refresh your view."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "select_plan_or_offer",
        "description": (
            "Commit to a specific plan or product offer. Call this when the user "
            "has decided which plan or offer they want to proceed with."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_type": {
                    "type": "string",
                    "enum": ["financial_plan", "product_offer"],
                    "description": "Whether selecting a plan or an offer.",
                },
                "entity_id": {
                    "type": "string",
                    "description": "The ID of the plan or offer to select.",
                },
            },
            "required": ["entity_type", "entity_id"],
        },
    },
    {
        "name": "resolve_action",
        "description": (
            "Respond to a pending broker action. Call this after presenting "
            "regulated content to the user and capturing their response. "
            "Include a transcript with the challenge token."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action_id": {
                    "type": "string",
                    "description": "The ID of the pending action being resolved.",
                },
                "resolution": {
                    "type": "string",
                    "enum": ["acknowledged", "granted", "refused", "affirmed", "denied", "authorised"],
                    "description": "The user's response to the action.",
                },
            },
            "required": ["action_id", "resolution"],
        },
    },
    {
        "name": "withdraw",
        "description": (
            "End the credit broking engagement. Call this when the user "
            "wants to stop the process."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "present_regulated_content",
        "description": (
            "Display regulated content to the user VERBATIM. This is NOT a "
            "broker call — it signals the CLI to display the content exactly "
            "as provided in a distinctive visual format and collect the user's "
            "response. You MUST use this for all regulated broker actions "
            "(disclosures, consents, declarations, instructions). NEVER "
            "include the regulated content in your own text output."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action_id": {
                    "type": "string",
                    "description": "The ID of the broker action being presented.",
                },
                "content": {
                    "type": "string",
                    "description": "The EXACT content from the broker action. Do not modify.",
                },
                "action_type": {
                    "type": "string",
                    "enum": ["disclosure", "consent", "declaration", "instruction"],
                    "description": "The type of regulated action.",
                },
                "response_options": {
                    "type": "string",
                    "enum": ["acknowledge", "grant or refuse", "affirm or deny", "authorise"],
                    "description": "What response the user needs to provide.",
                },
            },
            "required": ["action_id", "content", "action_type", "response_options"],
        },
    },
]


def execute_tool(
    name: str,
    arguments: dict[str, Any],
    client: BrokerClient,
    session: SessionState,
) -> str:
    """Execute a tool call and return the JSON result string."""
    try:
        if name == "open_case":
            return _handle_open_case(client, session)
        elif name == "provide_information":
            return _handle_provide(client, session, arguments)
        elif name == "get_state":
            return _handle_get_state(client, session)
        elif name == "select_plan_or_offer":
            return _handle_select(client, session, arguments)
        elif name == "resolve_action":
            return _handle_resolve(client, session, arguments)
        elif name == "withdraw":
            return _handle_withdraw(client, session)
        else:
            return json.dumps({"error": True, "detail": f"Unknown tool: {name}"})
    except BrokerError as e:
        return json.dumps({"error": True, "status_code": e.status_code, "detail": e.detail})


def _update_pending(session: SessionState, response_data: dict) -> None:
    """Update session with the pending action from a broker response."""
    session.pending_action = response_data.get("pending_action")
    if session.pending_action and session.pending_action.get("action_type") == "case_outcome":
        session.case_complete = True


def _handle_open_case(client: BrokerClient, session: SessionState) -> str:
    result = client.open_case(user_id=session.user_id)
    session.case_id = result.case_id
    data = result.model_dump(mode="json")
    _update_pending(session, data)
    return json.dumps(data)


def _handle_provide(client: BrokerClient, session: SessionState, args: dict) -> str:
    if not session.case_id:
        return json.dumps({"error": True, "detail": "No case open. Call open_case first."})
    challenge_token = session.pending_action.get("challenge_token") if session.pending_action else None
    transcript = session.transcript.flush(challenge_token)
    result = client.provide(
        case_id=session.case_id,
        facts=args.get("facts", []),
        attributes=args.get("attributes", []),
        goals=args.get("goals", []),
        transcript=transcript,
    )
    data = result.model_dump(mode="json")
    _update_pending(session, data)
    return json.dumps(data)


def _handle_get_state(client: BrokerClient, session: SessionState) -> str:
    if not session.case_id:
        return json.dumps({"error": True, "detail": "No case open. Call open_case first."})
    result = client.get_state(session.case_id)
    return json.dumps(result.model_dump(mode="json"))


def _handle_select(client: BrokerClient, session: SessionState, args: dict) -> str:
    if not session.case_id:
        return json.dumps({"error": True, "detail": "No case open. Call open_case first."})
    challenge_token = session.pending_action.get("challenge_token") if session.pending_action else None
    transcript = session.transcript.flush(challenge_token)
    result = client.select(
        case_id=session.case_id,
        entity_type=args["entity_type"],
        entity_id=args["entity_id"],
        transcript=transcript,
    )
    data = result.model_dump(mode="json")
    _update_pending(session, data)
    return json.dumps(data)


def _handle_resolve(client: BrokerClient, session: SessionState, args: dict) -> str:
    if not session.case_id:
        return json.dumps({"error": True, "detail": "No case open. Call open_case first."})
    challenge_token = session.pending_action.get("challenge_token") if session.pending_action else None
    transcript = session.transcript.flush(challenge_token)
    result = client.resolve(
        case_id=session.case_id,
        action_id=args["action_id"],
        resolution=args["resolution"],
        transcript=transcript,
    )
    data = result.model_dump(mode="json")
    _update_pending(session, data)
    return json.dumps(data)


def _handle_withdraw(client: BrokerClient, session: SessionState) -> str:
    if not session.case_id:
        return json.dumps({"error": True, "detail": "No case open."})
    result = client.withdraw(session.case_id)
    data = result.model_dump(mode="json")
    _update_pending(session, data)
    session.case_complete = True
    return json.dumps(data)
