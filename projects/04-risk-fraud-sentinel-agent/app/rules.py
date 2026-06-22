from __future__ import annotations

from .models import FraudFinding, Transaction


def evaluate_rules(transaction: Transaction) -> list[FraudFinding]:
    findings: list[FraudFinding] = []
    if transaction.amount > transaction.customer_avg_amount * 4:
        findings.append(
            FraudFinding(
                rule="Amount anomaly",
                severity="high",
                points=28,
                message="Transaction is more than 4x the customer's normal amount.",
                recommendation="Hold transaction and request customer confirmation.",
            )
        )
    if transaction.velocity_1h >= 6:
        findings.append(
            FraudFinding(
                rule="Velocity spike",
                severity="high",
                points=25,
                message="Customer has unusually high transaction frequency in the last hour.",
                recommendation="Temporarily limit additional transfers and review session activity.",
            )
        )
    if not transaction.device_trusted:
        findings.append(
            FraudFinding(
                rule="Untrusted device",
                severity="medium",
                points=16,
                message="Transaction originated from a device not previously associated with the customer.",
                recommendation="Trigger step-up authentication.",
            )
        )
    if transaction.country.lower() != "nigeria":
        findings.append(
            FraudFinding(
                rule="Geo anomaly",
                severity="medium",
                points=18,
                message="Transaction country differs from expected Nigeria operating region.",
                recommendation="Check travel profile and location history.",
            )
        )
    if transaction.hour < 5 and transaction.amount > transaction.customer_avg_amount * 2:
        findings.append(
            FraudFinding(
                rule="Unusual time",
                severity="medium",
                points=12,
                message="High-value transaction occurred during an unusual overnight window.",
                recommendation="Queue for analyst review if combined with other risk signals.",
            )
        )
    if transaction.prior_chargebacks > 0:
        findings.append(
            FraudFinding(
                rule="Chargeback history",
                severity="medium",
                points=10,
                message="Customer has previous chargeback or dispute history.",
                recommendation="Review prior dispute patterns before release.",
            )
        )
    if transaction.account_age_days < 30 and transaction.amount > 500000:
        findings.append(
            FraudFinding(
                rule="New account high value",
                severity="high",
                points=22,
                message="New account is attempting a high-value transaction.",
                recommendation="Require enhanced due diligence before processing.",
            )
        )
    return findings or [
        FraudFinding(
            rule="Baseline",
            severity="low",
            points=0,
            message="No major fraud indicators were detected.",
            recommendation="Allow transaction and continue passive monitoring.",
        )
    ]


def score_findings(findings: list[FraudFinding]) -> tuple[int, str, str]:
    score = max(0, min(100, sum(finding.points for finding in findings)))
    if score >= 75:
        return score, "critical", "block"
    if score >= 45:
        return score, "high", "manual_review"
    if score >= 20:
        return score, "medium", "step_up_auth"
    return score, "low", "allow"
