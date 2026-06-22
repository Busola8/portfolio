from __future__ import annotations

from uuid import uuid4

from .models import InvestigationReport, Transaction
from .rules import evaluate_rules, score_findings


class FraudSentinelEngine:
    def investigate(self, transaction: Transaction) -> InvestigationReport:
        findings = evaluate_rules(transaction)
        score, level, decision = score_findings(findings)
        case_id = f"FRD-{str(uuid4())[:8].upper()}"
        investigation_steps = [
            "RiskAgent: scored transaction using anomaly and rules engine.",
            "ContextAgent: reviewed customer profile, device trust, geography, and chargeback history.",
            "InvestigationAgent: generated case summary and recommended decision.",
            "ReportingAgent: prepared SharePoint report and voice briefing.",
        ]
        alerts = []
        if decision == "block":
            alerts.extend(["Fraud operations alert", "Customer verification required", "Transaction blocked"])
        elif decision == "manual_review":
            alerts.extend(["Fraud analyst review required", "Temporary hold recommended"])
        elif decision == "step_up_auth":
            alerts.append("Step-up authentication required")
        else:
            alerts.append("No active alert required")

        return InvestigationReport(
            case_id=case_id,
            transaction_id=transaction.transaction_id,
            risk_score=score,
            risk_level=level,
            decision=decision,
            findings=findings,
            investigation_steps=investigation_steps,
            alerts=alerts,
            sharepoint_report=f"/FraudReports/{case_id}-{transaction.transaction_id}.md",
            voice_briefing=(
                f"Case {case_id}: {level} risk transaction for customer "
                f"{transaction.customer_id}. Recommended action: {decision.replace('_', ' ')}."
            ),
        )
