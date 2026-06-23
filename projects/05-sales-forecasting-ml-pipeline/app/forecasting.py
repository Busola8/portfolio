from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from statistics import mean

from .models import DagTask, ForecastPoint, ForecastRequest, ModelMetrics, PipelineRun, SalesRecord


DEFAULT_SALES = [
    SalesRecord(month="2025-01", revenue=18500000, units=1320, marketing_spend=1200000, channel="retail"),
    SalesRecord(month="2025-02", revenue=19250000, units=1405, marketing_spend=1250000, channel="retail"),
    SalesRecord(month="2025-03", revenue=21400000, units=1520, marketing_spend=1380000, channel="online"),
    SalesRecord(month="2025-04", revenue=22150000, units=1588, marketing_spend=1420000, channel="online"),
    SalesRecord(month="2025-05", revenue=23600000, units=1660, marketing_spend=1500000, channel="partner"),
    SalesRecord(month="2025-06", revenue=24400000, units=1712, marketing_spend=1580000, channel="partner"),
    SalesRecord(month="2025-07", revenue=25950000, units=1830, marketing_spend=1650000, channel="retail"),
    SalesRecord(month="2025-08", revenue=26700000, units=1902, marketing_spend=1680000, channel="online"),
    SalesRecord(month="2025-09", revenue=28250000, units=1995, marketing_spend=1730000, channel="online"),
    SalesRecord(month="2025-10", revenue=30100000, units=2110, marketing_spend=1810000, channel="partner"),
    SalesRecord(month="2025-11", revenue=32600000, units=2290, marketing_spend=1900000, channel="retail"),
    SalesRecord(month="2025-12", revenue=37100000, units=2610, marketing_spend=2200000, channel="online"),
]


@dataclass(frozen=True)
class CandidateModel:
    name: str
    mae: float
    mape: float
    next_value: float


class ForecastingPipeline:
    def run(self, request: ForecastRequest) -> PipelineRun:
        records = request.records or DEFAULT_SALES
        values = [record.revenue for record in records]
        selected = self._select_model(values)
        drift_score = self._drift_score(values)
        drift_detected = drift_score >= request.drift_threshold
        retrain = drift_detected and request.retrain_if_drift
        forecast = self._forecast(records[-1].month, selected.next_value, values, request.horizon_months)

        tasks = [
            self._task("extract_sales_data", "Airflow", "success", 31, "raw/sales/monthly_sales.json"),
            self._task("prepare_features", "FeaturePipeline", "success", 44, "features/sales_features.parquet"),
            self._task("train_forecast_models", "ModelTrainer", "success", 88, "models/sales_forecaster.pkl"),
            self._task("evaluate_models", "Evaluator", "success", 23, "metrics/model_report.json"),
            self._task("publish_forecast", "ForecastService", "success", 18, "forecasts/revenue_forecast.json"),
            self._task("monitor_drift", "Monitoring", "warning" if drift_detected else "success", 14, "monitoring/drift_report.json"),
            self._task("trigger_retraining", "Airflow", "queued" if retrain else "skipped", 6, "dags/sales_forecasting_dag.py"),
        ]

        status = "retraining_queued" if retrain else "forecast_published"
        notes = [
            "Apache Airflow DAG coordinates ingestion, feature preparation, training, evaluation, publishing, monitoring, and retraining.",
            f"Best model selected by lowest MAPE: {selected.name}.",
            "Static demo mode can run on GitHub Pages; FastAPI returns the same pipeline contract when deployed.",
        ]
        if drift_detected:
            notes.append("Drift threshold breached; retraining branch is triggered for the next scheduled run.")
        else:
            notes.append("Drift is within tolerance; current model remains active.")

        return PipelineRun(
            run_id=f"sales-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            orchestration="Apache Airflow DAG: sales_forecasting_dag",
            status=status,
            summary=f"{request.horizon_months}-month revenue forecast published with {selected.name}; drift score {drift_score:.2f}.",
            tasks=tasks,
            metrics=ModelMetrics(
                selected_model=selected.name,
                mae=round(selected.mae, 2),
                mape=round(selected.mape, 3),
                drift_score=round(drift_score, 3),
                drift_detected=drift_detected,
                retraining_triggered=retrain,
            ),
            forecast=forecast,
            monitoring_notes=notes,
        )

    def _select_model(self, values: list[float]) -> CandidateModel:
        moving_average = mean(values[-3:])
        trend = mean([values[index] - values[index - 1] for index in range(1, len(values))])
        seasonal = values[-1] * 0.72 + values[-12] * 0.28 if len(values) >= 12 else values[-1]
        candidates = [
            CandidateModel("three_month_moving_average", self._mae(values[-3:], moving_average), self._mape(values[-3:], moving_average), moving_average + trend),
            CandidateModel("trend_regression_baseline", self._mae(values[-4:], values[-1]), self._mape(values[-4:], values[-1]), values[-1] + trend),
            CandidateModel("seasonal_naive_blend", self._mae(values[-3:], seasonal), self._mape(values[-3:], seasonal), seasonal + trend),
        ]
        return min(candidates, key=lambda item: item.mape)

    def _forecast(self, last_month: str, first_value: float, history: list[float], horizon: int) -> list[ForecastPoint]:
        year, month = [int(part) for part in last_month.split("-")]
        trend = mean([history[index] - history[index - 1] for index in range(1, len(history))])
        points = []
        for step in range(1, horizon + 1):
            month += 1
            if month > 12:
                year += 1
                month = 1
            seasonality = 1.08 if month in {11, 12} else 0.96 if month in {1, 2} else 1.0
            predicted = (first_value + trend * step) * seasonality
            spread = predicted * (0.08 + step * 0.01)
            points.append(
                ForecastPoint(
                    month=f"{year}-{month:02d}",
                    predicted_revenue=round(predicted, 2),
                    lower_bound=round(predicted - spread, 2),
                    upper_bound=round(predicted + spread, 2),
                )
            )
        return points

    def _drift_score(self, values: list[float]) -> float:
        baseline = mean(values[: max(3, len(values) // 2)])
        recent = mean(values[-3:])
        return abs(recent - baseline) / baseline

    def _mae(self, values: list[float], prediction: float) -> float:
        return mean([abs(value - prediction) for value in values])

    def _mape(self, values: list[float], prediction: float) -> float:
        return mean([abs(value - prediction) / value for value in values])

    def _task(self, task_id: str, owner: str, status: str, duration: int, artifact: str) -> DagTask:
        return DagTask(task_id=task_id, owner=owner, status=status, duration_seconds=duration, artifact=artifact)
