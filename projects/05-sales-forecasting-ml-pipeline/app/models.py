from __future__ import annotations

from pydantic import BaseModel, Field


class SalesRecord(BaseModel):
    month: str
    revenue: float = Field(gt=0)
    units: int = Field(gt=0)
    marketing_spend: float = Field(ge=0)
    channel: str


class ForecastRequest(BaseModel):
    horizon_months: int = Field(default=6, ge=1, le=12)
    drift_threshold: float = Field(default=0.18, ge=0.01, le=1.0)
    retrain_if_drift: bool = True
    records: list[SalesRecord] | None = None


class DagTask(BaseModel):
    task_id: str
    owner: str
    status: str
    duration_seconds: int
    artifact: str


class ForecastPoint(BaseModel):
    month: str
    predicted_revenue: float
    lower_bound: float
    upper_bound: float


class ModelMetrics(BaseModel):
    selected_model: str
    mae: float
    mape: float
    drift_score: float
    drift_detected: bool
    retraining_triggered: bool


class PipelineRun(BaseModel):
    run_id: str
    orchestration: str
    status: str
    summary: str
    tasks: list[DagTask]
    metrics: ModelMetrics
    forecast: list[ForecastPoint]
    monitoring_notes: list[str]
