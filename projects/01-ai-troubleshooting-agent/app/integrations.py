from __future__ import annotations

from typing import Any


class ExternalTelemetryAdapter:
    """Documents how real observability systems would replace sample JSON inputs."""

    def fetch_logs(self, service: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    def fetch_metrics(self, service: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError


class DatadogAdapter(ExternalTelemetryAdapter):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def fetch_logs(self, service: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError("Connect to Datadog Logs API with service filters.")

    def fetch_metrics(self, service: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError("Connect to Datadog Metrics API for latency/error rate.")


class PrometheusAdapter(ExternalTelemetryAdapter):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def fetch_logs(self, service: str | None = None) -> list[dict[str, Any]]:
        return []

    def fetch_metrics(self, service: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError("Query Prometheus HTTP API for service SLO metrics.")


class SplunkAdapter(ExternalTelemetryAdapter):
    def __init__(self, hec_url: str, hec_token: str) -> None:
        self.hec_url = hec_url
        self.hec_token = hec_token

    def fetch_logs(self, service: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError("Query Splunk Search API or HEC-backed indexes.")

    def fetch_metrics(self, service: str | None = None) -> list[dict[str, Any]]:
        return []
