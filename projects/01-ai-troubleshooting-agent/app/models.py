from pydantic import BaseModel, Field


class TroubleshootRequest(BaseModel):
    message: str = Field(..., min_length=3)
    session_id: str | None = None
    service: str | None = None
    severity: str | None = None


class EvidenceItem(BaseModel):
    title: str
    source: str
    score: float
    excerpt: str


class TroubleshootResponse(BaseModel):
    session_id: str
    summary: str
    likely_root_cause: str
    confidence: float
    remediation_steps: list[str]
    escalation: dict[str, str | bool]
    evidence: list[EvidenceItem]
    memory: list[str]
    used_llm: bool = False
    user_role: str = "demo"


class SessionState(BaseModel):
    session_id: str
    turns: list[str] = Field(default_factory=list)
