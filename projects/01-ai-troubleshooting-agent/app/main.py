from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .diagnostics import DiagnosticsEngine, build_root_cause
from .llm import build_llm_client
from .models import EvidenceItem, TroubleshootRequest, TroubleshootResponse
from .retrieval import KnowledgeRetriever
from .security import UserContext, enforce_rate_limit
from .settings import DATA_DIR, settings
from .storage import SQLiteSessionStore
from .telemetry import telemetry


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="AI Troubleshooting Agent",
    description="LLM-style RAG troubleshooting assistant with local diagnostics simulation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = KnowledgeRetriever(DATA_DIR / "knowledge_base.json", settings)
diagnostics = DiagnosticsEngine(DATA_DIR / "sample_logs.json", DATA_DIR / "metrics.json")
session_store = SQLiteSessionStore(settings)
llm_client = build_llm_client(settings)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/troubleshoot", response_model=TroubleshootResponse)
def troubleshoot(
    request: TroubleshootRequest,
    user: UserContext = Depends(enforce_rate_limit),
) -> TroubleshootResponse:
    session_id = request.session_id or str(uuid4())
    session = session_store.get_or_create(session_id)

    service = request.service or diagnostics.infer_service(request.message)
    snapshot = diagnostics.snapshot(service)
    query = " ".join(
        [
            request.message,
            " ".join(error["message"] for error in snapshot["recent_errors"]),
            snapshot["worst_metric"]["service"],
        ]
    )
    evidence = retriever.search(query)
    fallback = build_root_cause(
        request.message,
        snapshot,
        evidence,
    )
    root_cause, confidence, remediation = llm_client.generate_rca(
        request.message,
        snapshot,
        evidence,
        fallback,
    )

    summary = (
        f"Investigated {service or snapshot['worst_metric']['service']} using "
        f"{len(snapshot['recent_errors'])} error events and "
        f"{len(evidence)} retrieved knowledge articles."
    )
    should_escalate = confidence < 0.7 or request.severity == "critical"
    escalation = {
        "required": should_escalate,
        "target": "SRE on-call" if should_escalate else "Monitor in service queue",
        "reason": (
            "Critical severity or low confidence requires human review."
            if should_escalate
            else "Confidence is sufficient for first-line remediation."
        ),
    }

    session.turns.append(f"User: {request.message}")
    session.turns.append(f"Agent: {root_cause}")
    session.turns = session.turns[-8:]
    session_store.save(session)
    telemetry.event(
        "troubleshoot.completed",
        {
            "session_id": session_id,
            "service": service or snapshot["worst_metric"]["service"],
            "confidence": confidence,
            "escalated": should_escalate,
            "user_role": user.role,
            "openai_enabled": settings.openai_enabled,
            "vector_backend": settings.vector_backend,
        },
    )

    return TroubleshootResponse(
        session_id=session_id,
        summary=summary,
        likely_root_cause=root_cause,
        confidence=confidence,
        remediation_steps=remediation,
        escalation=escalation,
        evidence=[
            EvidenceItem(
                title=item["title"],
                source=item["source"],
                score=item["score"],
                excerpt=item["content"][:220],
            )
            for item in evidence
        ],
        memory=session.turns,
        used_llm=settings.openai_enabled,
        user_role=user.role,
    )
