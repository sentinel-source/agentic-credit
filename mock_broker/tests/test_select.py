from tests.helpers import advance_to_stage


def test_select_plan_produces_offers(client, case_id):
    advance_to_stage(client, case_id, target_stage=4)
    resp = client.post(f"/cases/{case_id}/select", json={
        "entity_type": "financial_plan",
        "entity_id": "plan-01",
    })
    assert resp.status_code == 200
    data = resp.json()
    event_types = [e["event_type"] for e in data["events"]]
    assert "offers_ready" in event_types
    assert data["pending_action"]["action_type"] == "disclosure"


def test_select_offer_produces_declaration(client, case_id):
    advance_to_stage(client, case_id, target_stage=6)
    resp = client.post(f"/cases/{case_id}/select", json={
        "entity_type": "product_offer",
        "entity_id": "offer-01",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["pending_action"]["action_type"] == "declaration"


def test_selected_offer_carried_to_instruction(client, case_id):
    """Selecting offer-02 (not the first) must produce an instruction referencing that offer."""
    advance_to_stage(client, case_id, target_stage=6)

    # Select the second offer, not the first
    resp = client.post(f"/cases/{case_id}/select", json={
        "entity_type": "product_offer",
        "entity_id": "offer-02",
    })
    assert resp.status_code == 200
    declaration_id = resp.json()["pending_action"]["id"]

    # Affirm the declaration
    resp = client.post(f"/cases/{case_id}/resolve", json={
        "action_id": declaration_id,
        "resolution": "affirmed",
    })
    assert resp.status_code == 200
    instruction = resp.json()["pending_action"]
    assert instruction["action_type"] == "instruction"

    # The instruction must reference offer-02, not offer-01
    subject_ids = [s["entity_id"] for s in instruction["subjects"]]
    assert "offer-02" in subject_ids
    assert "sterling" in instruction["information_scope"]["destination_url"][0].lower()
