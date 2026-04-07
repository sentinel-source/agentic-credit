def test_select_blocked_when_pending_action(client, case_id):
    """After open_case, there's an InformationRequest pending. Select should be blocked."""
    resp = client.post(f"/cases/{case_id}/select", json={
        "entity_type": "financial_plan",
        "entity_id": "plan-01",
    })
    assert resp.status_code == 409


def test_provide_allowed_during_information_request(client, case_id):
    """Provide is allowed when the pending action is an InformationRequest."""
    resp = client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f1", "fact_type": "gross_annual_income", "value": {"operator": "eq", "value": 35000}},
            {"id": "f2", "fact_type": "employment_status", "value": {"operator": "eq", "value": "employed"}},
        ],
        "goals": [
            {"id": "g1", "goal_type": "debt_consolidation"},
        ],
    })
    assert resp.status_code == 200


def test_provide_blocked_during_disclosure(client, case_id):
    """Provide is blocked when the pending action is a Disclosure (not InformationRequest)."""
    # Advance to stage 2 (disclosure pending)
    client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f1", "fact_type": "gross_annual_income", "value": {"operator": "eq", "value": 35000}},
            {"id": "f2", "fact_type": "employment_status", "value": {"operator": "eq", "value": "employed"}},
        ],
    })
    # Now a disclosure is pending — provide should be blocked
    resp = client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f3", "fact_type": "number_of_dependants", "value": {"operator": "eq", "value": 2}},
        ],
    })
    assert resp.status_code == 409


def test_get_state_always_allowed(client, case_id):
    """Get state works regardless of pending actions."""
    resp = client.get(f"/cases/{case_id}/state")
    assert resp.status_code == 200
