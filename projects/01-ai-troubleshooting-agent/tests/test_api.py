from fastapi.testclient import TestClient

from app.main import app


def test_troubleshoot_endpoint_returns_rca() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/troubleshoot",
        headers={"Authorization": "Bearer demo-analyst-token"},
        json={
            "message": "payments-api checkout requests are timing out with 503 errors",
            "severity": "high",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "Database connection pool" in payload["likely_root_cause"]
    assert payload["user_role"] == "analyst"
