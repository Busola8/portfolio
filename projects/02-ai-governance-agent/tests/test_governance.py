from app.models import AgentRecord
from app.orchestrator import GovernanceOrchestrator
from app.policies import analytics_checks, compliance_checks, privacy_checks, risk_score, value_metrics


def risky_agent() -> AgentRecord:
    return AgentRecord(
        agent_id="ai-troubleshooting-agent",
        agent_name="AI Troubleshooting Agent",
        owner="Platform Operations",
        department="Technology",
        model="gpt-4.1-mini",
        purpose="Diagnose incidents and recommend remediation.",
        permissions=["read", "write"],
        tools=["monitoring-api", "ticketing-api", "sharepoint"],
        data_classification="confidential",
        tasks_completed=420,
        human_interventions=65,
        avg_minutes_saved_per_task=18,
        monthly_token_cost_usd=240,
        active_users=75,
        decisions_made=120,
        explainability_enabled=False,
        audit_logging=True,
        automated_decisioning=True,
        pii_used=True,
        human_review=False,
        retention_days=90,
        region="Nigeria",
    )


def test_policy_checks_find_critical_controls() -> None:
    agent = risky_agent()
    findings = privacy_checks(agent) + compliance_checks(agent) + analytics_checks(agent)

    assert any(finding.severity == "critical" for finding in findings)
    assert any("human" in finding.recommendation.lower() for finding in findings)
    assert any("decision" in finding.control.lower() for finding in findings)


def test_risk_score_flags_high_risk() -> None:
    agent = risky_agent()
    response = GovernanceOrchestrator().evaluate("audit-1", agent, alert_threshold=75)

    assert response.compliance_score < 75
    assert response.alert_required is True
    assert response.risk_level in {"high", "critical"}
    assert response.automation_percentage > 80
    assert response.estimated_hours_saved > 100


def test_value_metrics_measure_agent_impact() -> None:
    value_score, automation_percentage, hours_saved = value_metrics(risky_agent())

    assert value_score > 0
    assert automation_percentage == 86.6
    assert hours_saved == 126.0


def test_risk_score_passes_low_risk_agent() -> None:
    agent = risky_agent().model_copy(
        update={
            "pii_used": False,
            "automated_decisioning": False,
            "human_review": True,
            "audit_logging": True,
            "explainability_enabled": True,
            "retention_days": 30,
            "active_users": 40,
            "data_classification": "internal",
            "region": "Nigeria",
            "permissions": ["read"],
            "tools": ["dashboard-api"],
            "monthly_token_cost_usd": 30,
        }
    )
    findings = GovernanceOrchestrator().evaluate("audit-2", agent, alert_threshold=75).findings
    score, risk = risk_score(findings)

    assert score >= 90
    assert risk == "low"
