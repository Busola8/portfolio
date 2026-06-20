from fastapi.testclient import TestClient

from app.main import app


def test_run_workflow_endpoint() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/workflows/run",
        json={
            "customer_name": "Adebayo Foods Limited",
            "documents": ["certificate_of_incorporation", "director_id"],
            "voice_channel": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["approval_required"] is True
    assert payload["assigned_queue"] == "Compliance Approval Queue"


def test_dashboard_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    assert "total_workflows" in response.json()
