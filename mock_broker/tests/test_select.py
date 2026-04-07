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
