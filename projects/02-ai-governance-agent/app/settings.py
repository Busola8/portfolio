from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv("APP_ENV", "local")
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'governance.db'}")
    auth_tokens: str = os.getenv("AUTH_TOKENS", "demo-governance-token:governance,exec-token:executive")
    alert_threshold: int = int(os.getenv("ALERT_THRESHOLD", "75"))
    langgraph_enabled: bool = os.getenv("LANGGRAPH_ENABLED", "false").lower() == "true"

    @property
    def token_roles(self) -> dict[str, str]:
        roles: dict[str, str] = {}
        for item in self.auth_tokens.split(","):
            if ":" not in item:
                continue
            token, role = item.split(":", 1)
            roles[token.strip()] = role.strip()
        return roles


settings = Settings()
