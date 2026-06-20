from __future__ import annotations

from uuid import uuid4

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import DashboardSummary, GovernanceRequest, GovernanceResponse
from .orchestrator import GovernanceOrchestrator
from .security import UserContext, get_current_user
from .settings import settings
from .storage import AuditStore


app = FastAPI(
    title="AI Governance Agent",
    description="Multi-agent AI governance, policy validation, audit, and risk dashboard.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

store = AuditStore(settings)
orchestrator = GovernanceOrchestrator()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "Agent Governance and Analytics Platform",
        "status": "live",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/evaluate", response_model=GovernanceResponse)
def evaluate(
    request: GovernanceRequest,
    user: UserContext = Depends(get_current_user),
) -> GovernanceResponse:
    audit_id = str(uuid4())
    response = orchestrator.evaluate(audit_id, request.agent, settings.alert_threshold)
    response.workflow_trace.insert(0, f"AccessControl: request accepted for role {user.role}")
    store.save(response)
    return response


@app.get("/api/dashboard", response_model=DashboardSummary)
def dashboard(user: UserContext = Depends(get_current_user)) -> DashboardSummary:
    return DashboardSummary(**store.summary())
