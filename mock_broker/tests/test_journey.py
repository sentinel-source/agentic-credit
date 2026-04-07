"""End-to-end test walking the complete personal loan journey."""


def test_full_happy_path(client):
    # Stage 0: Open case
    resp = client.post("/cases", json={"user_id": "user-journey-001"})
    assert resp.status_code == 201
    data = resp.json()
    case_id = data["case_id"]
    assert data["pending_action"]["action_type"] == "information_request"

    # Stage 1: Provide financial data
    resp = client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f1", "fact_type": "gross_annual_income", "value": {"operator": "eq", "value": 35000}},
            {"id": "f2", "fact_type": "employment_status", "value": {"operator": "eq", "value": "employed"}},
            {"id": "f3", "fact_type": "existing_credit_card_balance", "value": {"operator": "eq", "value": 3000}},
            {"id": "f4", "fact_type": "existing_loan_balance", "value": {"operator": "eq", "value": 0}},
        ],
        "attributes": [
            {"id": "a1", "attribute_type": "full_name", "value": "Jane Smith"},
            {"id": "a2", "attribute_type": "date_of_birth", "value": "1990-05-15"},
        ],
        "goals": [
            {"id": "g1", "goal_type": "debt_consolidation", "statement": "Consolidate my credit card debt"},
        ],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["pending_action"]["action_type"] == "disclosure"
    disclosure_id = data["pending_action"]["id"]

    # Stage 2: Acknowledge broker disclosure
    resp = client.post(f"/cases/{case_id}/resolve", json={
        "action_id": disclosure_id,
        "resolution": "acknowledged",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["pending_action"]["action_type"] == "consent"
    consent_id = data["pending_action"]["id"]

    # Stage 3: Grant consent for credit search
    resp = client.post(f"/cases/{case_id}/resolve", json={
        "action_id": consent_id,
        "resolution": "granted",
    })
    assert resp.status_code == 200
    data = resp.json()
    event_types = [e["event_type"] for e in data["events"]]
    assert "plans_ready" in event_types
    assert data["pending_action"] is None

    # Verify plans in state
    state = client.get(f"/cases/{case_id}/state").json()
    assert len(state["plans"]) == 2
    assert state["plans"][0]["suitability_assessment"]["suitable"] is True

    # Stage 4: Select a plan
    resp = client.post(f"/cases/{case_id}/select", json={
        "entity_type": "financial_plan",
        "entity_id": "plan-01",
    })
    assert resp.status_code == 200
    data = resp.json()
    event_types = [e["event_type"] for e in data["events"]]
    assert "offers_ready" in event_types
    assert data["pending_action"]["action_type"] == "disclosure"
    offer_disclosure_id = data["pending_action"]["id"]

    # Verify offers in state
    state = client.get(f"/cases/{case_id}/state").json()
    assert len(state["offers"]) == 3

    # Stage 5: Acknowledge offer disclosure
    resp = client.post(f"/cases/{case_id}/resolve", json={
        "action_id": offer_disclosure_id,
        "resolution": "acknowledged",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["pending_action"] is None

    # Stage 6: Select an offer
    resp = client.post(f"/cases/{case_id}/select", json={
        "entity_type": "product_offer",
        "entity_id": "offer-01",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["pending_action"]["action_type"] == "declaration"
    declaration_id = data["pending_action"]["id"]

    # Stage 7: Affirm declaration
    resp = client.post(f"/cases/{case_id}/resolve", json={
        "action_id": declaration_id,
        "resolution": "affirmed",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["pending_action"]["action_type"] == "instruction"
    instruction_id = data["pending_action"]["id"]

    # Stage 8: Authorise instruction (proceed to lender)
    resp = client.post(f"/cases/{case_id}/resolve", json={
        "action_id": instruction_id,
        "resolution": "authorised",
    })
    assert resp.status_code == 200
    data = resp.json()
    event_types = [e["event_type"] for e in data["events"]]
    assert "case_status_changed" in event_types
    assert data["pending_action"]["action_type"] == "case_outcome"

    # Verify terminal state
    state = client.get(f"/cases/{case_id}/state").json()
    assert state["status"] == "transferred"

    # Verify no further operations allowed
    resp = client.post(f"/cases/{case_id}/withdraw")
    assert resp.status_code == 409
