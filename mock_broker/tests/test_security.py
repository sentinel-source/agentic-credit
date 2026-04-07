"""Tests for security features: challenge tokens, session binding, URL signing, version tracking."""

from tests.helpers import advance_to_stage


# --- Transcript challenge tokens ---

def test_challenge_token_present_in_broker_actions(client):
    resp = client.post("/cases", json={"user_id": "user-sec-001"})
    action = resp.json()["pending_action"]
    assert "challenge_token" in action
    assert len(action["challenge_token"]) > 0


def test_challenge_token_verified_when_present_in_transcript(client):
    resp = client.post("/cases", json={"user_id": "user-sec-002"})
    case_id = resp.json()["case_id"]
    token = resp.json()["pending_action"]["challenge_token"]

    # Include the challenge token in the transcript
    client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f1", "fact_type": "gross_annual_income", "value": {"operator": "eq", "value": 35000}},
            {"id": "f2", "fact_type": "employment_status", "value": {"operator": "eq", "value": "employed"}},
        ],
        "transcript": f"User provided income info. Token: {token}",
    })
    state = client.get(f"/cases/{case_id}/state").json()
    provide_entry = next(e for e in state["evidence"] if e["operation"] == "provide")
    assert provide_entry["challenge_token_verified"] is True
    assert provide_entry["transcript_hash"] is not None


def test_challenge_token_fails_when_missing_from_transcript(client):
    resp = client.post("/cases", json={"user_id": "user-sec-003"})
    case_id = resp.json()["case_id"]

    client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f1", "fact_type": "gross_annual_income", "value": {"operator": "eq", "value": 35000}},
        ],
        "transcript": "User provided income info but no token here.",
    })
    state = client.get(f"/cases/{case_id}/state").json()
    provide_entry = next(e for e in state["evidence"] if e["operation"] == "provide")
    assert provide_entry["challenge_token_verified"] is False


def test_no_transcript_means_no_verification(client):
    resp = client.post("/cases", json={"user_id": "user-sec-004"})
    case_id = resp.json()["case_id"]

    client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f1", "fact_type": "gross_annual_income", "value": {"operator": "eq", "value": 35000}},
        ],
    })
    state = client.get(f"/cases/{case_id}/state").json()
    provide_entry = next(e for e in state["evidence"] if e["operation"] == "provide")
    assert provide_entry["challenge_token_verified"] is None
    assert provide_entry["transcript_hash"] is None


# --- Session binding ---

def test_duplicate_user_rejected(client):
    client.post("/cases", json={"user_id": "user-sec-dup"})
    resp = client.post("/cases", json={"user_id": "user-sec-dup"})
    assert resp.status_code == 409
    assert "already has an open case" in resp.json()["detail"]


def test_user_can_open_new_case_after_withdrawal(client):
    resp = client.post("/cases", json={"user_id": "user-sec-reopen"})
    case_id = resp.json()["case_id"]
    client.post(f"/cases/{case_id}/withdraw")
    # Now should be able to open a new case
    resp2 = client.post("/cases", json={"user_id": "user-sec-reopen"})
    assert resp2.status_code == 201


# --- HMAC-signed redirect URLs ---

def test_instruction_contains_redirect_token(client):
    resp = client.post("/cases", json={"user_id": "user-sec-url"})
    case_id = resp.json()["case_id"]
    advance_to_stage(client, case_id, target_stage=8)
    state = client.get(f"/cases/{case_id}/state").json()
    action = state["pending_action"]
    assert action["action_type"] == "instruction"
    assert "redirect_token" in (action.get("information_scope") or {})


def test_verify_endpoint_validates_correct_token(client):
    resp = client.post("/cases", json={"user_id": "user-sec-verify"})
    case_id = resp.json()["case_id"]
    advance_to_stage(client, case_id, target_stage=8)
    state = client.get(f"/cases/{case_id}/state").json()
    scope = state["pending_action"]["information_scope"]
    token = scope["redirect_token"][0]
    url = scope["destination_url"][0]
    offer_id = scope["offer_id"][0]

    resp = client.post("/verify", json={
        "token": token,
        "case_id": case_id,
        "offer_id": offer_id,
        "destination_url": url,
    })
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


def test_verify_endpoint_rejects_tampered_url(client):
    resp = client.post("/cases", json={"user_id": "user-sec-tamper"})
    case_id = resp.json()["case_id"]
    advance_to_stage(client, case_id, target_stage=8)
    state = client.get(f"/cases/{case_id}/state").json()
    scope = state["pending_action"]["information_scope"]
    token = scope["redirect_token"][0]
    offer_id = scope["offer_id"][0]

    resp = client.post("/verify", json={
        "token": token,
        "case_id": case_id,
        "offer_id": offer_id,
        "destination_url": "https://evil.example.com/phish",
    })
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


# --- User Agent version tracking ---

def test_ua_version_recorded_in_evidence(client):
    resp = client.post("/cases", json={"user_id": "user-sec-ver1"},
                       headers={"X-UA-Version": "agent-v1.0"})
    case_id = resp.json()["case_id"]
    state = client.get(f"/cases/{case_id}/state").json()
    assert state["evidence"][0]["ua_version"] == "agent-v1.0"
    assert state["evidence"][0]["ua_version_mismatch"] is False


def test_ua_version_mismatch_detected(client):
    resp = client.post("/cases", json={"user_id": "user-sec-ver2"},
                       headers={"X-UA-Version": "agent-v1.0"})
    case_id = resp.json()["case_id"]

    # Provide with a different version
    client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f1", "fact_type": "gross_annual_income", "value": {"operator": "eq", "value": 35000}},
        ],
    }, headers={"X-UA-Version": "agent-v2.0"})

    state = client.get(f"/cases/{case_id}/state").json()
    provide_entry = next(e for e in state["evidence"] if e["operation"] == "provide")
    assert provide_entry["ua_version"] == "agent-v2.0"
    assert provide_entry["ua_version_mismatch"] is True
