from __future__ import annotations

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    account_age_days: int
    amount: float
    currency: str = "NGN"
    merchant: str
    channel: str
    country: str = "Nigeria"
    hour: int
    device_trusted: bool
    prior_chargebacks: int
    velocity_1h: int
    customer_avg_amount: float


class FraudFinding(BaseModel):
    rule: str
    severity: str
    points: int
    message: str
    recommendation: str


class InvestigationReport(BaseModel):
    case_id: str
    transaction_id: str
    risk_score: int
    risk_level: str
    decision: str
    findings: list[FraudFinding]
    investigation_steps: list[str]
    alerts: list[str]
    sharepoint_report: str
    voice_briefing: str


class TransactionBatch(BaseModel):
    transactions: list[Transaction] = Field(default_factory=list)


class DashboardSummary(BaseModel):
    total_cases: int
    blocked: int
    review_required: int
    average_risk_score: float
    latest_cases: list[dict[str, str | int | float]]
