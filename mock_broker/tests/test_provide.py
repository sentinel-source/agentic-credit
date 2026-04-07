def test_provide_resolves_info_request(client, case_id):
    resp = client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f1", "fact_type": "gross_annual_income", "value": {"operator": "eq", "value": 35000}},
            {"id": "f2", "fact_type": "employment_status", "value": {"operator": "eq", "value": "employed"}},
            {"id": "f3", "fact_type": "existing_credit_card_balance", "value": {"operator": "eq", "value": 3000}},
            {"id": "f4", "fact_type": "existing_loan_balance", "value": {"operator": "eq", "value": 0}},
        ],
        "goals": [
            {"id": "g1", "goal_type": "debt_consolidation", "statement": "Consolidate credit card debt"},
        ],
    })
    assert resp.status_code == 200
    data = resp.json()
    event_types = [e["event_type"] for e in data["events"]]
    assert "profile_updated" in event_types
    # After providing data, broker should issue disclosure
    assert data["pending_action"]["action_type"] == "disclosure"


def test_provide_not_found(client):
    resp = client.post("/cases/nonexistent/provide", json={"facts": []})
    assert resp.status_code == 404
