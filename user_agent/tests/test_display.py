import json
from unittest.mock import patch

from user_agent.display import handle_regulated_content


def test_acknowledge_disclosure():
    with patch("builtins.input", return_value=""):
        result = handle_regulated_content({
            "action_type": "disclosure",
            "content": "Broker is regulated by FCA.",
            "response_options": "acknowledge",
        })
    data = json.loads(result)
    assert data["user_response"] == "acknowledged"
    assert data["displayed_verbatim"] is True


def test_grant_consent():
    with patch("builtins.input", return_value="yes"):
        result = handle_regulated_content({
            "action_type": "consent",
            "content": "Do you consent to a credit search?",
            "response_options": "grant or refuse",
        })
    data = json.loads(result)
    assert data["user_response"] == "granted"


def test_refuse_consent():
    with patch("builtins.input", return_value="no"):
        result = handle_regulated_content({
            "action_type": "consent",
            "content": "Do you consent to a credit search?",
            "response_options": "grant or refuse",
        })
    data = json.loads(result)
    assert data["user_response"] == "refused"


def test_affirm_declaration():
    with patch("builtins.input", return_value="yes"):
        result = handle_regulated_content({
            "action_type": "declaration",
            "content": "I confirm the info is true.",
            "response_options": "affirm or deny",
        })
    data = json.loads(result)
    assert data["user_response"] == "affirmed"


def test_deny_declaration():
    with patch("builtins.input", return_value="no"):
        result = handle_regulated_content({
            "action_type": "declaration",
            "content": "I confirm the info is true.",
            "response_options": "affirm or deny",
        })
    data = json.loads(result)
    assert data["user_response"] == "denied"


def test_authorise_instruction():
    with patch("builtins.input", return_value="yes"):
        result = handle_regulated_content({
            "action_type": "instruction",
            "content": "Proceed to lender website.",
            "response_options": "authorise",
        })
    data = json.loads(result)
    assert data["user_response"] == "authorised"


def test_refuse_instruction():
    with patch("builtins.input", return_value="no"):
        result = handle_regulated_content({
            "action_type": "instruction",
            "content": "Proceed to lender website.",
            "response_options": "authorise",
        })
    data = json.loads(result)
    assert data["user_response"] == "refused"


def test_case_outcome_no_response():
    result = handle_regulated_content({
        "action_type": "case_outcome",
        "content": "Case is complete.",
        "response_options": "none",
    })
    data = json.loads(result)
    assert data["user_response"] == "none"
