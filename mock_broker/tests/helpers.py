"""Helpers to drive a case through the scripted journey to a target stage."""

from __future__ import annotations


def _provide_data(client, case_id: str):
    client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f1", "fact_type": "gross_annual_income", "value": {"operator": "eq", "value": 35000}},
            {"id": "f2", "fact_type": "employment_status", "value": {"operator": "eq", "value": "employed"}},
            {"id": "f3", "fact_type": "existing_credit_card_balance", "value": {"operator": "eq", "value": 3000}},
            {"id": "f4", "fact_type": "existing_loan_balance", "value": {"operator": "eq", "value": 0}},
            {"id": "f5", "fact_type": "net_monthly_income", "value": {"operator": "eq", "value": 2400}},
            {"id": "f6", "fact_type": "monthly_expenditure", "value": {"operator": "eq", "value": 1200}},
        ],
        "attributes": [
            {"id": "a1", "attribute_type": "full_name", "value": "Jane Smith"},
            {"id": "a2", "attribute_type": "date_of_birth", "value": "1990-05-15"},
        ],
        "goals": [
            {"id": "g1", "goal_type": "debt_consolidation", "statement": "Consolidate my credit card debt"},
        ],
    })


def _resolve(client, case_id: str, resolution: str):
    state = client.get(f"/cases/{case_id}/state").json()
    action_id = state["pending_action"]["id"]
    client.post(f"/cases/{case_id}/resolve", json={
        "action_id": action_id,
        "resolution": resolution,
    })


def advance_to_stage(client, case_id: str, target_stage: int):
    """Drive the journey from stage 1 (case already opened) to the target stage.

    Stage mapping:
      1 → case opened, info request pending
      2 → data provided, disclosure pending
      3 → disclosure acknowledged, consent pending
      4 → consent granted, plans ready (no gate)
      5 → plan selected, offer disclosure pending
      6 → offer disclosure acknowledged (no gate)
      7 → offer selected, declaration pending
      8 → declaration affirmed, instruction pending
    """
    if target_stage >= 2:
        _provide_data(client, case_id)
    if target_stage >= 3:
        _resolve(client, case_id, "acknowledged")
    if target_stage >= 4:
        _resolve(client, case_id, "granted")
    if target_stage >= 5:
        client.post(f"/cases/{case_id}/select", json={
            "entity_type": "financial_plan",
            "entity_id": "plan-01",
        })
    if target_stage >= 6:
        _resolve(client, case_id, "acknowledged")
    if target_stage >= 7:
        client.post(f"/cases/{case_id}/select", json={
            "entity_type": "product_offer",
            "entity_id": "offer-01",
        })
    if target_stage >= 8:
        _resolve(client, case_id, "affirmed")
