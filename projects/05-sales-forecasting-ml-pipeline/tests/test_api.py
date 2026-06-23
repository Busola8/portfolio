from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_pipeline_endpoint():
    response = client.post("/api/pipeline/run", json={"horizon_months": 3, "drift_threshold": 0.18})

    assert response.status_code == 200
    payload = response.json()
    assert payload["orchestration"] == "Apache Airflow DAG: sales_forecasting_dag"
    assert len(payload["forecast"]) == 3
