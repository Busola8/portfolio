# Sales Forecasting ML Pipeline

A runnable demand and revenue forecasting project that demonstrates MLOps orchestration with Apache Airflow, model evaluation, forecast publishing, drift monitoring, and retraining control.

## What It Includes

- FastAPI backend with `/api/pipeline/run` and `/api/sample-sales`
- Browser dashboard that works with the backend or in static GitHub Pages fallback mode
- Actual Airflow DAG file in `dags/sales_forecasting_dag.py`
- Deterministic forecasting engine with model selection, MAPE/MAE metrics, drift score, and retraining branch
- Tests for API behavior and pipeline logic
- Docker-ready deployment files

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8040
```

Then open:

```text
frontend/index.html
```

## Airflow DAG

The Airflow DAG is intentionally included as source code rather than required for the public demo. Recruiters can inspect the orchestration design without needing to run an Airflow scheduler.

Tasks:

1. `extract_sales_data`
2. `prepare_features`
3. `train_forecast_models`
4. `evaluate_models`
5. `publish_forecast`
6. `monitor_drift`
7. `trigger_retraining`

## Recruiter Demo Mode

If FastAPI is not running, the frontend runs a browser-only static pipeline simulation. This keeps the project usable on GitHub Pages while preserving the same shape as the backend API response.
