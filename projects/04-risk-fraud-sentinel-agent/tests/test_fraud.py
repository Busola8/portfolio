from app.engine import FraudSentinelEngine
from app.models import Transaction
from app.rules import evaluate_rules, score_findings


def risky_transaction() -> Transaction:
    return Transaction(
        transaction_id="TXN-9001",
        customer_id="CUST-1044",
        account_age_days=18,
        amount=1250000,
        merchant="Electronics Hub",
        channel="mobile",
        country="Nigeria",
        hour=2,
        device_trusted=False,
        prior_chargebacks=1,
        velocity_1h=7,
        customer_avg_amount=150000,
    )


def test_rules_detect_high_risk_transaction() -> None:
    findings = evaluate_rules(risky_transaction())
    score, level, decision = score_findings(findings)

    assert score >= 75
    assert level == "critical"
    assert decision == "block"
    assert any(finding.rule == "Velocity spike" for finding in findings)


def test_engine_generates_investigation_report() -> None:
    report = FraudSentinelEngine().investigate(risky_transaction())

    assert report.risk_level == "critical"
    assert report.decision == "block"
    assert report.sharepoint_report.startswith("/FraudReports/")
    assert report.voice_briefing


def test_low_risk_transaction_is_allowed() -> None:
    report = FraudSentinelEngine().investigate(
        Transaction(
            transaction_id="TXN-9002",
            customer_id="CUST-2088",
            account_age_days=740,
            amount=45000,
            merchant="Groceries Direct",
            channel="pos",
            country="Nigeria",
            hour=14,
            device_trusted=True,
            prior_chargebacks=0,
            velocity_1h=1,
            customer_avg_amount=52000,
        )
    )

    assert report.risk_level == "low"
    assert report.decision == "allow"
