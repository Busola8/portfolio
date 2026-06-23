from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .forecasting import DEFAULT_SALES, ForecastingPipeline
from .models import ForecastRequest, PipelineRun, SalesRecord


app = FastAPI(
    title="Sales Forecasting ML Pipeline",
    description="Demand and revenue forecasting pipeline with Airflow-style orchestration, model evaluation, drift monitoring, and retraining.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = ForecastingPipeline()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "Sales Forecasting ML Pipeline",
        "status": "live",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/sample-sales", response_model=list[SalesRecord])
def sample_sales() -> list[SalesRecord]:
    return DEFAULT_SALES


@app.post("/api/pipeline/run", response_model=PipelineRun)
def run_pipeline(request: ForecastRequest) -> PipelineRun:
    return pipeline.run(request)
