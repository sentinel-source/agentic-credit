"""Tests for consent refused and declaration denied paths."""

from tests.helpers import advance_to_stage


def test_consent_refused_declines_case(client):
    resp = client.post("/cases", json={"user_id": "user-refuse-001"})
    case_id = resp.json()["case_id"]
    advance_to_stage(client, case_id, target_stage=3)

    # Refuse consent
    state = client.get(f"/cases/{case_id}/state").json()
    action_id = state["pending_action"]["id"]
    resp = client.post(f"/cases/{case_id}/resolve", json={
        "action_id": action_id,
        "resolution": "refused",
    })
    assert resp.status_code == 200
    data = resp.json()

    # Should emit case_status_changed and a case_outcome action
    event_types = [e["event_type"] for e in data["events"]]
    assert "case_status_changed" in event_types
    assert data["pending_action"]["action_type"] == "case_outcome"

    # Verify terminal state
    state = client.get(f"/cases/{case_id}/state").json()
    assert state["status"] == "declined"

    # No further operations allowed
    resp = client.post(f"/cases/{case_id}/provide", json={"facts": []})
    assert resp.status_code == 409


def test_consent_refused_no_plans_generated(client):
    resp = client.post("/cases", json={"user_id": "user-refuse-002"})
    case_id = resp.json()["case_id"]
    advance_to_stage(client, case_id, target_stage=3)

    state = client.get(f"/cases/{case_id}/state").json()
    action_id = state["pending_action"]["id"]
    client.post(f"/cases/{case_id}/resolve", json={
        "action_id": action_id,
        "resolution": "refused",
    })

    state = client.get(f"/cases/{case_id}/state").json()
    assert state["plans"] == []
    assert state["offers"] == []


def test_declaration_denied_declines_case(client):
    resp = client.post("/cases", json={"user_id": "user-deny-001"})
    case_id = resp.json()["case_id"]
    advance_to_stage(client, case_id, target_stage=7)

    # Deny declaration
    state = client.get(f"/cases/{case_id}/state").json()
    action_id = state["pending_action"]["id"]
    resp = client.post(f"/cases/{case_id}/resolve", json={
        "action_id": action_id,
        "resolution": "denied",
    })
    assert resp.status_code == 200
    data = resp.json()

    event_types = [e["event_type"] for e in data["events"]]
    assert "case_status_changed" in event_types
    assert data["pending_action"]["action_type"] == "case_outcome"

    state = client.get(f"/cases/{case_id}/state").json()
    assert state["status"] == "declined"


def test_declaration_denied_preserves_offers(client):
    """Offers should still be visible in state even after decline."""
    resp = client.post("/cases", json={"user_id": "user-deny-002"})
    case_id = resp.json()["case_id"]
    advance_to_stage(client, case_id, target_stage=7)

    state = client.get(f"/cases/{case_id}/state").json()
    action_id = state["pending_action"]["id"]
    client.post(f"/cases/{case_id}/resolve", json={
        "action_id": action_id,
        "resolution": "denied",
    })

    state = client.get(f"/cases/{case_id}/state").json()
    assert len(state["plans"]) > 0
    assert len(state["offers"]) > 0


def test_user_can_reopen_after_consent_refused(client):
    resp = client.post("/cases", json={"user_id": "user-refuse-reopen"})
    case_id = resp.json()["case_id"]
    advance_to_stage(client, case_id, target_stage=3)

    state = client.get(f"/cases/{case_id}/state").json()
    action_id = state["pending_action"]["id"]
    client.post(f"/cases/{case_id}/resolve", json={
        "action_id": action_id,
        "resolution": "refused",
    })

    # Should be able to start fresh
    resp2 = client.post("/cases", json={"user_id": "user-refuse-reopen"})
    assert resp2.status_code == 201
