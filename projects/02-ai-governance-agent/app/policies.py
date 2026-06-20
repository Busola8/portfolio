from __future__ import annotations

from .models import AgentRecord, PolicyFinding


def privacy_checks(agent: AgentRecord) -> list[PolicyFinding]:
    findings: list[PolicyFinding] = []
    if agent.pii_used and agent.retention_days > 90:
        findings.append(
            PolicyFinding(
                agent="PrivacyAgent",
                control="PII retention",
                status="fail",
                severity="high",
                message="PII retention exceeds the 90-day governance threshold.",
                recommendation="Reduce retention, document lawful basis, or apply anonymization.",
            )
        )
    if agent.pii_used and not agent.human_review and agent.automated_decisioning:
        findings.append(
            PolicyFinding(
                agent="PrivacyAgent",
                control="Human review",
                status="fail",
                severity="critical",
                message="Automated decisions using PII lack human review.",
                recommendation="Add human-in-the-loop approval for impacted decisions.",
            )
        )
    return findings or [
        PolicyFinding(
            agent="PrivacyAgent",
            control="Privacy baseline",
            status="pass",
            severity="low",
            message="Privacy controls meet baseline checks.",
            recommendation="Continue scheduled privacy review.",
        )
    ]


def security_checks(agent: AgentRecord) -> list[PolicyFinding]:
    findings: list[PolicyFinding] = []
    if not agent.audit_logging:
        findings.append(
            PolicyFinding(
                agent="SecurityAgent",
                control="Prompt audit logging",
                status="fail",
                severity="medium",
                message="Prompt and response activity is not logged for auditability.",
                recommendation="Enable redacted prompt logging with access controls.",
            )
        )
    high_risk_tools = {"banking-api", "sharepoint", "approval-engine", "telephony"}
    if agent.data_classification.lower() in {"restricted", "confidential"} and agent.region != "Nigeria":
        findings.append(
            PolicyFinding(
                agent="SecurityAgent",
                control="Data residency",
                status="review",
                severity="medium",
                message="Sensitive data is processed outside Nigeria.",
                recommendation="Confirm NDPR/data residency expectations and regional routing.",
            )
        )
    if high_risk_tools.intersection({tool.lower() for tool in agent.tools}) and "write" in {
        permission.lower() for permission in agent.permissions
    }:
        findings.append(
            PolicyFinding(
                agent="AccessAgent",
                control="Privileged tool access",
                status="review",
                severity="high",
                message="Agent has write access to high-impact operational tools.",
                recommendation="Require owner approval, scoped credentials, and break-glass logging.",
            )
        )
    return findings or [
        PolicyFinding(
            agent="SecurityAgent",
            control="Security baseline",
            status="pass",
            severity="low",
            message="Security controls meet baseline checks.",
            recommendation="Maintain logging and access review cadence.",
        )
    ]


def compliance_checks(agent: AgentRecord) -> list[PolicyFinding]:
    findings: list[PolicyFinding] = []
    if agent.automated_decisioning and not agent.human_review:
        findings.append(
            PolicyFinding(
                agent="ComplianceAgent",
                control="Automated decisioning",
                status="fail",
                severity="critical",
                message="Automated decisioning is enabled without documented human oversight.",
                recommendation="Add documented review, appeal, and exception handling controls.",
            )
        )
    if agent.active_users > 10000 and agent.data_classification.lower() != "public":
        findings.append(
            PolicyFinding(
                agent="ComplianceAgent",
                control="Scale review",
                status="review",
                severity="medium",
                message="Large-scale AI activity requires enhanced governance review.",
                recommendation="Route to AI governance council before production expansion.",
            )
        )
    return findings or [
        PolicyFinding(
            agent="ComplianceAgent",
            control="Compliance baseline",
            status="pass",
            severity="low",
            message="Compliance checks pass for declared use case.",
            recommendation="Keep policy evidence attached to the model record.",
        )
    ]


def analytics_checks(agent: AgentRecord) -> list[PolicyFinding]:
    findings: list[PolicyFinding] = []
    if agent.tasks_completed < 10 and agent.monthly_token_cost_usd > 100:
        findings.append(
            PolicyFinding(
                agent="ValueAgent",
                control="Low adoption high cost",
                status="review",
                severity="medium",
                message="Agent has low usage relative to monthly model cost.",
                recommendation="Review adoption, retire the agent, or route it to higher-value workflows.",
            )
        )
    if agent.decisions_made > 0 and not agent.explainability_enabled:
        findings.append(
            PolicyFinding(
                agent="ExplainabilityAgent",
                control="Decision traceability",
                status="fail",
                severity="high",
                message="Agent makes decisions without explainability enabled.",
                recommendation="Store decision rationale, evidence, model version, and tool call trace.",
            )
        )
    return findings or [
        PolicyFinding(
            agent="ValueAgent",
            control="Value baseline",
            status="pass",
            severity="low",
            message="Agent adoption and value metrics meet baseline expectations.",
            recommendation="Continue monitoring usage, cost, and intervention trends.",
        )
    ]


def value_metrics(agent: AgentRecord) -> tuple[int, float, float]:
    total_work = agent.tasks_completed + agent.human_interventions
    automation_percentage = 0.0 if total_work == 0 else (agent.tasks_completed / total_work) * 100
    hours_saved = (agent.tasks_completed * agent.avg_minutes_saved_per_task) / 60
    cost_penalty = min(agent.monthly_token_cost_usd / 20, 20)
    intervention_penalty = 100 - automation_percentage
    value_score = int(max(0, min(100, 60 + hours_saved / 5 - cost_penalty - intervention_penalty / 8)))
    return value_score, round(automation_percentage, 1), round(hours_saved, 1)


def risk_score(findings: list[PolicyFinding]) -> tuple[int, str]:
    penalties = {"critical": 30, "high": 22, "medium": 12, "low": 2}
    score = 100 - sum(penalties.get(finding.severity, 5) for finding in findings if finding.status != "pass")
    score = max(0, min(score, 100))
    if score < 55:
        return score, "critical"
    if score < 75:
        return score, "high"
    if score < 90:
        return score, "medium"
    return score, "low"
