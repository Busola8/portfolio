from pathlib import Path

from app.diagnostics import DiagnosticsEngine, build_root_cause
from app.retrieval import KnowledgeRetriever


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


RETRIEVAL_CASES = [
    ("checkout latency database pool payments-api", "payments-api"),
    ("invalid token login failures identity", "identity-service"),
    ("oom killed pdf batch memory", "document-worker"),
]


def test_retrieval_top_result_matches_expected_service() -> None:
    retriever = KnowledgeRetriever(DATA_DIR / "knowledge_base.json")

    matches = 0
    for query, expected_service in RETRIEVAL_CASES:
        result = retriever.search(query, limit=1)[0]
        matches += int(result["service"] == expected_service)

    assert matches / len(RETRIEVAL_CASES) >= 0.9


def test_rca_expected_failure_classes() -> None:
    diagnostics = DiagnosticsEngine(
        DATA_DIR / "sample_logs.json",
        DATA_DIR / "metrics.json",
    )
    cases = [
        ("payments-api", "checkout 503 timeout", "Database connection pool"),
        ("document-worker", "worker oom during pdf extraction", "memory leak"),
        ("identity-service", "login 401 invalid token", "Authentication failures"),
    ]

    for service, message, expected_phrase in cases:
        snapshot = diagnostics.snapshot(service)
        root_cause, confidence, remediation = build_root_cause(message, snapshot, [])
        assert expected_phrase.lower() in root_cause.lower()
        assert confidence >= 0.75
        assert len(remediation) >= 3
