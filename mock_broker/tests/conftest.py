import pytest
from fastapi.testclient import TestClient

from mock_broker.app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def case_id(client):
    """Open a case and return its ID."""
    resp = client.post("/cases", json={"user_id": "test-user-001"})
    return resp.json()["case_id"]
