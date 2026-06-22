from __future__ import annotations

from collections import deque

from .models import InvestigationReport


class CaseStore:
    def __init__(self) -> None:
        self.cases: deque[InvestigationReport] = deque(maxlen=100)

    def save(self, report: InvestigationReport) -> None:
        self.cases.appendleft(report)

    def summary(self) -> dict:
        if not self.cases:
            return {
                "total_cases": 0,
                "blocked": 0,
                "review_required": 0,
                "average_risk_score": 0,
                "latest_cases": [],
            }
        total = len(self.cases)
        return {
            "total_cases": total,
            "blocked": sum(1 for case in self.cases if case.decision == "block"),
            "review_required": sum(1 for case in self.cases if case.decision == "manual_review"),
            "average_risk_score": round(sum(case.risk_score for case in self.cases) / total, 1),
            "latest_cases": [
                {
                    "case_id": case.case_id,
                    "transaction_id": case.transaction_id,
                    "risk_score": case.risk_score,
                    "risk_level": case.risk_level,
                    "decision": case.decision,
                }
                for case in list(self.cases)[:6]
            ],
        }
