from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Troubleshooting Agent"
    environment: str = os.getenv("APP_ENV", "local")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    vector_backend: str = os.getenv("VECTOR_BACKEND", "local")
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'sessions.db'}")
    auth_tokens: str = os.getenv(
        "AUTH_TOKENS",
        "demo-analyst-token:analyst,demo-admin-token:admin",
    )
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    telemetry_backend: str = os.getenv("TELEMETRY_BACKEND", "local")
    datadog_api_key: str | None = os.getenv("DATADOG_API_KEY")
    splunk_hec_url: str | None = os.getenv("SPLUNK_HEC_URL")
    splunk_hec_token: str | None = os.getenv("SPLUNK_HEC_TOKEN")
    prometheus_url: str | None = os.getenv("PROMETHEUS_URL")

    @property
    def openai_enabled(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def token_roles(self) -> dict[str, str]:
        pairs: dict[str, str] = {}
        for item in self.auth_tokens.split(","):
            if ":" not in item:
                continue
            token, role = item.split(":", 1)
            pairs[token.strip()] = role.strip()
        return pairs


settings = Settings()
