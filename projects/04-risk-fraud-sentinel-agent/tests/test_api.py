from fastapi.testclient import TestClient

from app.main import app
from tests.test_fraud import risky_transaction


def test_investigate_endpoint() -> None:
    client = TestClient(app)
    response = client.post("/api/investigate", json=risky_transaction().model_dump())

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "block"
    assert payload["risk_score"] >= 75


def test_dashboard_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    assert "total_cases" in response.json()
