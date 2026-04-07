def test_get_state_after_open(client, case_id):
    resp = client.get(f"/cases/{case_id}/state")
    assert resp.status_code == 200
    data = resp.json()
    assert data["case_id"] == case_id
    assert data["status"] == "open"
    assert data["pending_action"] is not None


def test_get_state_is_idempotent(client, case_id):
    r1 = client.get(f"/cases/{case_id}/state")
    r2 = client.get(f"/cases/{case_id}/state")
    assert r1.json()["status"] == r2.json()["status"]
    assert r1.json()["pending_action"] == r2.json()["pending_action"]


def test_get_state_not_found(client):
    resp = client.get("/cases/nonexistent/state")
    assert resp.status_code == 404
