from __future__ import annotations

from .models import AgentRecord, GovernanceResponse, PolicyFinding
from .policies import analytics_checks, compliance_checks, privacy_checks, risk_score, security_checks, value_metrics


class GovernanceOrchestrator:
    """Local deterministic orchestration mirroring a LangGraph agent workflow."""

    def evaluate(self, audit_id: str, agent: AgentRecord, alert_threshold: int) -> GovernanceResponse:
        trace = [
            "RegistryAgent: normalized identity, owner, department, permissions, and tools",
            "UsageAgent: measured completed tasks, human interventions, adoption, and cost",
            "PrivacyAgent: evaluated PII, retention, and Nigeria data handling controls",
            "AccessAgent: evaluated permissions and high-impact tool access",
            "ComplianceAgent: evaluated automated decisioning and scale controls",
            "ExplainabilityAgent: evaluated decision traceability",
            "RiskAgent: calculated governance risk, value score, and alert decision",
        ]
        findings: list[PolicyFinding] = []
        findings.extend(privacy_checks(agent))
        findings.extend(security_checks(agent))
        findings.extend(compliance_checks(agent))
        findings.extend(analytics_checks(agent))
        score, risk_level = risk_score(findings)
        value_score, automation_percentage, hours_saved = value_metrics(agent)
        alert_required = score < alert_threshold or risk_level in {"critical", "high"}
        failed = [finding for finding in findings if finding.status != "pass"]
        executive_summary = (
            f"{agent.agent_name} in {agent.department} scored {score}/100 governance, "
            f"{value_score}/100 value, and {automation_percentage}% automation. "
            f"{len(failed)} controls require attention."
        )
        return GovernanceResponse(
            audit_id=audit_id,
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            department=agent.department,
            compliance_score=score,
            risk_level=risk_level,
            alert_required=alert_required,
            value_score=value_score,
            automation_percentage=automation_percentage,
            estimated_hours_saved=hours_saved,
            agent_metrics={
                "tasks_completed": agent.tasks_completed,
                "human_interventions": agent.human_interventions,
                "monthly_token_cost_usd": agent.monthly_token_cost_usd,
                "active_users": agent.active_users,
                "decisions_made": agent.decisions_made,
            },
            executive_summary=executive_summary,
            findings=findings,
            workflow_trace=trace,
        )
