from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path

from .models import GovernanceResponse
from .settings import DATA_DIR, Settings


logger = logging.getLogger("governance-agent.storage")


class AuditStore:
    def __init__(self, settings: Settings) -> None:
        self.db_path = self._resolve_path(settings.database_url)
        self.memory_connection: sqlite3.Connection | None = None
        if str(self.db_path) == ":memory:":
            self.memory_connection = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._initialize()
        except sqlite3.OperationalError as exc:
            logger.warning("Falling back to in-memory audit store: %s", exc)
            self.db_path = Path(":memory:")
            self.memory_connection = sqlite3.connect(":memory:", check_same_thread=False)
            self._initialize()

    @staticmethod
    def _resolve_path(database_url: str) -> Path:
        if database_url.startswith("sqlite:///"):
            raw_path = database_url.replace("sqlite:///", "", 1)
            if raw_path == ":memory:":
                return Path(":memory:")
            return Path(raw_path)
        return DATA_DIR / "governance.db"

    def _connect(self) -> sqlite3.Connection:
        if self.memory_connection is not None:
            return self.memory_connection
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        connection = self._connect()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audits (
                audit_id TEXT PRIMARY KEY,
                system TEXT NOT NULL,
                score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                alert_required INTEGER NOT NULL,
                payload TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()

    def save(self, response: GovernanceResponse) -> None:
        connection = self._connect()
        connection.execute(
            """
            INSERT INTO audits (audit_id, system, score, risk_level, alert_required, payload)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                response.audit_id,
                response.agent_name,
                response.compliance_score,
                response.risk_level,
                int(response.alert_required),
                response.model_dump_json(),
            ),
        )
        connection.commit()

    def summary(self) -> dict:
        connection = self._connect()
        rows = connection.execute(
            "SELECT score, risk_level, alert_required, payload FROM audits ORDER BY created_at DESC"
        ).fetchall()
        if not rows:
            return {
                "total_audits": 0,
                "average_score": 0,
                "high_risk_count": 0,
                "total_tasks_completed": 0,
                "total_human_interventions": 0,
                "total_estimated_hours_saved": 0,
                "total_monthly_token_cost_usd": 0,
                "average_automation_percentage": 0,
                "top_departments": [],
                "latest_alerts": [],
            }
        scores = [row[0] for row in rows]
        high_risk_count = sum(1 for row in rows if row[1] in {"critical", "high"})
        total_tasks_completed = 0
        total_human_interventions = 0
        total_estimated_hours_saved = 0.0
        total_monthly_token_cost_usd = 0.0
        automation_values: list[float] = []
        department_hours: dict[str, float] = {}
        latest_alerts = []
        for _, _, _, payload in rows:
            data = json.loads(payload)
            metrics = data.get("agent_metrics", {})
            total_tasks_completed += int(metrics.get("tasks_completed", 0))
            total_human_interventions += int(metrics.get("human_interventions", 0))
            total_monthly_token_cost_usd += float(metrics.get("monthly_token_cost_usd", 0))
            total_estimated_hours_saved += float(data.get("estimated_hours_saved", 0))
            automation_values.append(float(data.get("automation_percentage", 0)))
            department = data.get("department", "Unassigned")
            department_hours[department] = department_hours.get(department, 0.0) + float(
                data.get("estimated_hours_saved", 0)
            )
        for score, risk_level, alert_required, payload in rows[:5]:
            data = json.loads(payload)
            latest_alerts.append(
                {
                    "audit_id": data["audit_id"],
                    "agent_name": data["agent_name"],
                    "score": score,
                    "risk_level": risk_level,
                    "alert_required": bool(alert_required),
                    "summary": data["executive_summary"],
                }
            )
        return {
            "total_audits": len(rows),
            "average_score": round(sum(scores) / len(scores), 1),
            "high_risk_count": high_risk_count,
            "total_tasks_completed": total_tasks_completed,
            "total_human_interventions": total_human_interventions,
            "total_estimated_hours_saved": round(total_estimated_hours_saved, 1),
            "total_monthly_token_cost_usd": round(total_monthly_token_cost_usd, 2),
            "average_automation_percentage": round(sum(automation_values) / len(automation_values), 1),
            "top_departments": [
                {"department": department, "estimated_hours_saved": round(hours, 1)}
                for department, hours in sorted(
                    department_hours.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )[:5]
            ],
            "latest_alerts": latest_alerts,
        }
