from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .engine import WorkflowEngine
from .models import DashboardSummary, WorkflowRequest, WorkflowResponse
from .storage import WorkflowStore


app = FastAPI(
    title="AI-Powered Workflow Automation Agent",
    description="Enterprise onboarding, KYC, document, approval, and notification workflow automation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = WorkflowEngine()
store = WorkflowStore()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "AI-Powered Workflow Automation Agent",
        "status": "live",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/workflows/run", response_model=WorkflowResponse)
def run_workflow(request: WorkflowRequest) -> WorkflowResponse:
    response = engine.run(str(uuid4()), request)
    store.save(response)
    return response


@app.get("/api/dashboard", response_model=DashboardSummary)
def dashboard() -> DashboardSummary:
    return DashboardSummary(**store.summary())
