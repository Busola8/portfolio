# Architecture

```text
Sales sources
    |
    v
Airflow DAG: sales_forecasting_dag
    |
    +--> extract_sales_data
    +--> prepare_features
    +--> train_forecast_models
    +--> evaluate_models
    +--> publish_forecast
    +--> monitor_drift
    +--> trigger_retraining
    |
    v
FastAPI demo API
    |
    v
Portfolio frontend dashboard
```

## Design Notes

- Airflow owns scheduling and task dependency structure.
- The FastAPI app exposes a recruiter-friendly run endpoint and mirrors the artifacts a production pipeline would publish.
- Forecasting uses deterministic baseline models so the demo is portable and does not require heavy ML packages.
- Drift monitoring controls whether retraining is queued.

## Production Path

- Replace local sample data with warehouse or lakehouse inputs.
- Persist features, models, and forecasts in object storage or a feature store.
- Add MLflow or a model registry for model versioning.
- Run the DAG in managed Airflow, Astronomer, MWAA, or Cloud Composer.
- Export metrics to Prometheus, Grafana, or a BI dashboard.
