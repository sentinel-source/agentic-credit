def test_withdraw(client, case_id):
    resp = client.post(f"/cases/{case_id}/withdraw")
    assert resp.status_code == 200
    data = resp.json()
    event_types = [e["event_type"] for e in data["events"]]
    assert "case_status_changed" in event_types
    assert data["pending_action"]["action_type"] == "case_outcome"

    # Verify case is now terminal
    state = client.get(f"/cases/{case_id}/state").json()
    assert state["status"] == "withdrawn"


def test_withdraw_terminal_case_rejected(client, case_id):
    client.post(f"/cases/{case_id}/withdraw")
    resp = client.post(f"/cases/{case_id}/withdraw")
    assert resp.status_code == 409
