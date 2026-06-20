from __future__ import annotations

from pydantic import BaseModel, Field


class WorkflowRequest(BaseModel):
    customer_name: str
    customer_type: str = "SME"
    country: str = "Nigeria"
    risk_level: str = "medium"
    documents: list[str] = Field(default_factory=list)
    requested_products: list[str] = Field(default_factory=list)
    voice_channel: bool = False
    sharepoint_folder: str | None = None


class WorkflowStep(BaseModel):
    agent: str
    action: str
    status: str
    details: str


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    approval_required: bool
    assigned_queue: str
    completion_percentage: int
    summary: str
    steps: list[WorkflowStep]
    documents_created: list[str]
    notifications: list[str]
    n8n_replacement_notes: list[str]


class DashboardSummary(BaseModel):
    total_workflows: int
    auto_approved: int
    approval_required: int
    average_completion: float
    latest: list[dict[str, str | int | bool]]
