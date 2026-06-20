from fastapi.testclient import TestClient

from app.main import app
from tests.test_governance import risky_agent


def test_evaluate_endpoint_returns_governance_result() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/evaluate",
        headers={"Authorization": "Bearer demo-governance-token"},
        json={"agent": risky_agent().model_dump()},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_name"] == "AI Troubleshooting Agent"
    assert payload["alert_required"] is True
    assert payload["compliance_score"] < 75
    assert payload["automation_percentage"] > 80


def test_dashboard_returns_agent_analytics_summary() -> None:
    client = TestClient(app)
    response = client.get(
        "/api/dashboard",
        headers={"Authorization": "Bearer exec-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "total_audits" in payload
    assert "average_automation_percentage" in payload
    assert "top_departments" in payload
