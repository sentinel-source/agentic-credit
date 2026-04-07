def test_open_case_with_user_id(client):
    resp = client.post("/cases", json={"user_id": "user-open-001"})
    assert resp.status_code == 201
    data = resp.json()
    assert "case_id" in data
    assert data["pending_action"]["action_type"] == "information_request"


def test_open_case_with_initial_facts(client):
    resp = client.post("/cases", json={
        "user_id": "user-open-002",
        "facts": [
            {
                "id": "f1",
                "fact_type": "gross_annual_income",
                "value": {"operator": "eq", "value": 35000},
            }
        ],
        "goals": [
            {
                "id": "g1",
                "goal_type": "debt_consolidation",
                "statement": "I want to consolidate my debts",
            }
        ],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["events"]) >= 1
    event_types = [e["event_type"] for e in data["events"]]
    assert "profile_updated" in event_types
    assert "goals_updated" in event_types


def test_open_case_returns_unique_ids(client):
    r1 = client.post("/cases", json={"user_id": "user-open-003"})
    r2 = client.post("/cases", json={"user_id": "user-open-004"})
    assert r1.json()["case_id"] != r2.json()["case_id"]


def test_open_case_rejects_duplicate_user(client):
    client.post("/cases", json={"user_id": "user-dup-001"})
    resp = client.post("/cases", json={"user_id": "user-dup-001"})
    assert resp.status_code == 409


def test_open_case_requires_user_id(client):
    resp = client.post("/cases", json={})
    assert resp.status_code == 422
