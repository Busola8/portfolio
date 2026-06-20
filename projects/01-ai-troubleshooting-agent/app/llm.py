from __future__ import annotations

import json
import logging
from typing import Any

from .settings import Settings


logger = logging.getLogger("troubleshooting-agent.llm")


class LLMClient:
    def generate_rca(
        self,
        message: str,
        snapshot: dict[str, Any],
        evidence: list[dict[str, Any]],
        fallback: tuple[str, float, list[str]],
    ) -> tuple[str, float, list[str]]:
        raise NotImplementedError


class LocalLLMClient(LLMClient):
    def generate_rca(
        self,
        message: str,
        snapshot: dict[str, Any],
        evidence: list[dict[str, Any]],
        fallback: tuple[str, float, list[str]],
    ) -> tuple[str, float, list[str]]:
        return fallback


class OpenAILLMClient(LLMClient):
    def __init__(self, settings: Settings) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def generate_rca(
        self,
        message: str,
        snapshot: dict[str, Any],
        evidence: list[dict[str, Any]],
        fallback: tuple[str, float, list[str]],
    ) -> tuple[str, float, list[str]]:
        fallback_root_cause, fallback_confidence, fallback_steps = fallback
        prompt = {
            "incident": message,
            "diagnostics": snapshot,
            "retrieved_evidence": evidence,
            "fallback_analysis": {
                "root_cause": fallback_root_cause,
                "confidence": fallback_confidence,
                "remediation_steps": fallback_steps,
            },
        }
        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are an SRE incident analysis assistant. Return only JSON "
                            "with keys root_cause, confidence, and remediation_steps. "
                            "Do not invent evidence beyond the supplied logs, metrics, and runbooks."
                        ),
                    },
                    {"role": "user", "content": json.dumps(prompt)},
                ],
            )
            text = response.output_text
            payload = json.loads(text)
        except Exception as exc:
            logger.warning("OpenAI RCA unavailable; using local fallback: %s", exc)
            return fallback

        root_cause = str(payload.get("root_cause") or fallback_root_cause)
        confidence = float(payload.get("confidence") or fallback_confidence)
        steps = payload.get("remediation_steps") or fallback_steps
        if not isinstance(steps, list):
            steps = fallback_steps
        return root_cause, max(0.0, min(confidence, 1.0)), [str(step) for step in steps]


def build_llm_client(settings: Settings) -> LLMClient:
    if settings.openai_enabled:
        return OpenAILLMClient(settings)
    return LocalLLMClient()
