from pathlib import Path

from app.diagnostics import DiagnosticsEngine, build_root_cause
from app.retrieval import KnowledgeRetriever


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def test_retriever_prioritizes_database_runbook() -> None:
    retriever = KnowledgeRetriever(DATA_DIR / "knowledge_base.json")
    results = retriever.search("payments-api database connection pool exhausted")

    assert results[0]["service"] == "payments-api"
    assert results[0]["score"] > 0


def test_diagnostics_identifies_database_root_cause() -> None:
    diagnostics = DiagnosticsEngine(
        DATA_DIR / "sample_logs.json",
        DATA_DIR / "metrics.json",
    )
    snapshot = diagnostics.snapshot("payments-api")
    root_cause, confidence, steps = build_root_cause(
        "checkout is timing out with 503 errors",
        snapshot,
        [{"title": "API database connection pool exhaustion"}],
    )

    assert "Database connection pool" in root_cause
    assert confidence >= 0.8
    assert steps
