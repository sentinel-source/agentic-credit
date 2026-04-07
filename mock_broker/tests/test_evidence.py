def test_evidence_recorded_on_open(client):
    resp = client.post("/cases", json={})
    case_id = resp.json()["case_id"]
    state = client.get(f"/cases/{case_id}/state").json()
    assert len(state["evidence"]) == 1
    assert state["evidence"][0]["operation"] == "open_case"


def test_evidence_recorded_on_provide(client, case_id):
    client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f1", "fact_type": "gross_annual_income", "value": {"operator": "eq", "value": 35000}},
        ],
    })
    state = client.get(f"/cases/{case_id}/state").json()
    ops = [e["operation"] for e in state["evidence"]]
    assert "open_case" in ops
    assert "provide" in ops


def test_transcript_stored_in_evidence(client, case_id):
    client.post(f"/cases/{case_id}/provide", json={
        "facts": [
            {"id": "f1", "fact_type": "gross_annual_income", "value": {"operator": "eq", "value": 35000}},
        ],
        "transcript": "User said: I earn thirty-five thousand a year.",
    })
    state = client.get(f"/cases/{case_id}/state").json()
    provide_entry = next(e for e in state["evidence"] if e["operation"] == "provide")
    assert provide_entry["transcript"] == "User said: I earn thirty-five thousand a year."


def test_evidence_accumulates_through_journey(client):
    from tests.helpers import advance_to_stage

    resp = client.post("/cases", json={})
    case_id = resp.json()["case_id"]
    advance_to_stage(client, case_id, target_stage=5)

    state = client.get(f"/cases/{case_id}/state").json()
    ops = [e["operation"] for e in state["evidence"]]
    assert "open_case" in ops
    assert "provide" in ops
    assert "resolve_action" in ops
    assert "select" in ops
    assert len(state["evidence"]) >= 5
