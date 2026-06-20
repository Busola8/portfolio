from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DiagnosticsEngine:
    def __init__(self, logs_path: Path, metrics_path: Path) -> None:
        self.logs = self._load(logs_path)["logs"]
        self.metrics = self._load(metrics_path)["metrics"]

    @staticmethod
    def _load(path: Path) -> dict[str, Any]:
        with path.open(encoding="utf-8") as file:
            return json.load(file)

    def snapshot(self, service: str | None = None) -> dict[str, Any]:
        service_logs = [
            item for item in self.logs if service is None or item["service"] == service
        ]
        service_metrics = [
            item for item in self.metrics if service is None or item["service"] == service
        ]
        if not service_logs:
            service_logs = self.logs
        if not service_metrics:
            service_metrics = self.metrics

        recent_errors = [
            item for item in service_logs if item["level"].lower() in {"error", "critical"}
        ][-6:]
        worst_metric = max(
            service_metrics,
            key=lambda item: item.get("error_rate", 0) + item.get("latency_ms", 0) / 1000,
        )

        return {
            "recent_errors": recent_errors,
            "worst_metric": worst_metric,
            "services_seen": sorted({item["service"] for item in service_logs}),
        }

    def infer_service(self, text: str) -> str | None:
        lowered = text.lower()
        services = {item["service"] for item in self.logs} | {
            item["service"] for item in self.metrics
        }
        for service in services:
            if service.lower() in lowered:
                return service
        return None


def build_root_cause(
    message: str,
    diagnostic_snapshot: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> tuple[str, float, list[str]]:
    combined = " ".join(
        [
            message,
            " ".join(error["message"] for error in diagnostic_snapshot["recent_errors"]),
            " ".join(item["title"] for item in evidence),
        ]
    ).lower()

    if "database" in combined or "connection" in combined or "pool" in combined:
        return (
            "Database connection pool exhaustion is causing request timeouts.",
            0.86,
            [
                "Check active database connections and pool saturation.",
                "Scale the API workers only after increasing database max connections safely.",
                "Restart stuck workers after draining traffic from the affected instance.",
                "Add connection timeout and pool usage alerts for early detection.",
            ],
        )

    if "memory" in combined or "oom" in combined or "leak" in combined:
        return (
            "A memory leak or oversized batch job is exhausting container memory.",
            0.82,
            [
                "Inspect memory trend for the affected service over the last deployment window.",
                "Roll back the most recent release if memory growth started after deployment.",
                "Reduce batch size and add heap/container memory alerts.",
                "Capture a memory profile before recycling the unhealthy pods.",
            ],
        )

    if "auth" in combined or "token" in combined or "401" in combined:
        return (
            "Authentication failures are likely caused by expired credentials or token validation drift.",
            0.78,
            [
                "Verify identity provider availability and token signing key rotation.",
                "Check clock synchronization between API nodes and the auth provider.",
                "Refresh service credentials and replay a failed request in staging.",
                "Escalate to the identity team if failures span multiple applications.",
            ],
        )

    return (
        "The issue appears to be a service degradation with correlated errors and latency spikes.",
        0.64,
        [
            "Review the highest-error service in the metrics snapshot.",
            "Compare the incident start time with recent deployments and dependency changes.",
            "Enable additional request tracing for the affected endpoint.",
            "Escalate if customer impact continues beyond the next monitoring interval.",
        ],
    )
