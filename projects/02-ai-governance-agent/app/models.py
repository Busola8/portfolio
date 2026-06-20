from __future__ import annotations

from pydantic import BaseModel, Field


class AgentRecord(BaseModel):
    agent_id: str
    agent_name: str
    owner: str
    department: str
    model: str
    purpose: str
    permissions: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    data_classification: str
    tasks_completed: int
    human_interventions: int
    avg_minutes_saved_per_task: float
    monthly_token_cost_usd: float
    decisions_made: int
    explainability_enabled: bool
    audit_logging: bool
    active_users: int
    automated_decisioning: bool
    pii_used: bool
    human_review: bool
    retention_days: int
    region: str = "Nigeria"


class PolicyFinding(BaseModel):
    agent: str
    control: str
    status: str
    severity: str
    message: str
    recommendation: str


class GovernanceRequest(BaseModel):
    agent: AgentRecord


class GovernanceResponse(BaseModel):
    audit_id: str
    agent_id: str
    agent_name: str
    department: str
    compliance_score: int
    risk_level: str
    alert_required: bool
    value_score: int
    automation_percentage: float
    estimated_hours_saved: float
    agent_metrics: dict[str, int | float] = Field(default_factory=dict)
    executive_summary: str
    findings: list[PolicyFinding]
    workflow_trace: list[str]


class DashboardSummary(BaseModel):
    total_audits: int
    average_score: float
    high_risk_count: int
    total_tasks_completed: int
    total_human_interventions: int
    total_estimated_hours_saved: float
    total_monthly_token_cost_usd: float
    average_automation_percentage: float
    top_departments: list[dict[str, str | int | float]]
    latest_alerts: list[dict[str, str | int | bool]]
