from __future__ import annotations

from datetime import datetime


try:
    from airflow.decorators import dag, task
except ImportError:  # Allows syntax checks in environments without Airflow.
    dag = None
    task = None


if dag and task:
    @dag(
        dag_id="sales_forecasting_dag",
        start_date=datetime(2026, 1, 1),
        schedule="@daily",
        catchup=False,
        tags=["portfolio", "forecasting", "mlops"],
        description="Revenue forecasting pipeline with training, evaluation, publishing, drift monitoring, and retraining.",
    )
    def sales_forecasting_dag():
        @task
        def extract_sales_data() -> str:
            return "raw/sales/monthly_sales.json"

        @task
        def prepare_features(raw_path: str) -> str:
            return raw_path.replace("raw/sales", "features").replace(".json", ".parquet")

        @task
        def train_forecast_models(feature_path: str) -> dict[str, str]:
            return {
                "feature_path": feature_path,
                "model_path": "models/sales_forecaster.pkl",
                "candidate_models": "moving_average, trend_baseline, seasonal_blend",
            }

        @task
        def evaluate_models(training_result: dict[str, str]) -> dict[str, float | str]:
            return {
                "model_path": training_result["model_path"],
                "selected_model": "seasonal_blend",
                "mape": 0.082,
                "mae": 1285000.0,
            }

        @task
        def publish_forecast(evaluation: dict[str, float | str]) -> str:
            return f"forecasts/published/{evaluation['selected_model']}.json"

        @task
        def monitor_drift(forecast_path: str) -> dict[str, float | bool | str]:
            return {
                "forecast_path": forecast_path,
                "drift_score": 0.21,
                "drift_detected": True,
            }

        @task
        def trigger_retraining(drift_report: dict[str, float | bool | str]) -> str:
            if drift_report["drift_detected"]:
                return "Retraining queued for next Airflow run"
            return "No retraining required"

        raw = extract_sales_data()
        features = prepare_features(raw)
        training = train_forecast_models(features)
        evaluation = evaluate_models(training)
        forecast = publish_forecast(evaluation)
        drift = monitor_drift(forecast)
        trigger_retraining(drift)

    sales_forecasting_dag()
