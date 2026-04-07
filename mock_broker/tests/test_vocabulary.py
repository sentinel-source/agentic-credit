def test_fact_types(client):
    resp = client.get("/vocabulary/fact-types")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    for item in data:
        assert "name" in item
        assert "description" in item
        assert "examples" in item


def test_attribute_types(client):
    resp = client.get("/vocabulary/attribute-types")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0


def test_goal_types(client):
    resp = client.get("/vocabulary/goal-types")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    names = [g["name"] for g in data]
    assert "debt_consolidation" in names
    assert "major_purchase" in names
