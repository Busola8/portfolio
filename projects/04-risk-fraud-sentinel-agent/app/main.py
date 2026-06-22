from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .engine import FraudSentinelEngine
from .models import DashboardSummary, InvestigationReport, Transaction, TransactionBatch
from .storage import CaseStore


app = FastAPI(
    title="AI Risk & Fraud Sentinel Agent",
    description="Real-time fraud monitoring, anomaly scoring, investigation, and alerting demo.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = FraudSentinelEngine()
store = CaseStore()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "AI Risk & Fraud Sentinel Agent",
        "status": "live",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/investigate", response_model=InvestigationReport)
def investigate(transaction: Transaction) -> InvestigationReport:
    report = engine.investigate(transaction)
    store.save(report)
    return report


@app.post("/api/monitor", response_model=list[InvestigationReport])
def monitor(batch: TransactionBatch) -> list[InvestigationReport]:
    reports = [engine.investigate(transaction) for transaction in batch.transactions]
    for report in reports:
        store.save(report)
    return reports


@app.get("/api/dashboard", response_model=DashboardSummary)
def dashboard() -> DashboardSummary:
    return DashboardSummary(**store.summary())
