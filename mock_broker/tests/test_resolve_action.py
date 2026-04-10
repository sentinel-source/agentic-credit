from tests.helpers import advance_to_stage


def test_resolve_disclosure(client, case_id):
    advance_to_stage(client, case_id, target_stage=2)
    state = client.get(f"/cases/{case_id}/state").json()
    action_id = state["pending_action"]["id"]
    resp = client.post(f"/cases/{case_id}/resolve", json={
        "action_id": action_id,
        "resolution": "acknowledged",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["pending_action"]["action_type"] == "consent"


def test_resolve_consent(client, case_id):
    advance_to_stage(client, case_id, target_stage=3)
    state = client.get(f"/cases/{case_id}/state").json()
    action_id = state["pending_action"]["id"]
    resp = client.post(f"/cases/{case_id}/resolve", json={
        "action_id": action_id,
        "resolution": "granted",
    })
    assert resp.status_code == 200
    data = resp.json()
    event_types = [e["event_type"] for e in data["events"]]
    assert "plans_ready" in event_types
    assert data["pending_action"] is None


def test_resolve_wrong_action_id(client, case_id):
    advance_to_stage(client, case_id, target_stage=2)
    resp = client.post(f"/cases/{case_id}/resolve", json={
        "action_id": "wrong-id",
        "resolution": "acknowledged",
    })
    assert resp.status_code == 400
