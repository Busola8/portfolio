from app.security import InMemoryRateLimiter
from app.settings import Settings
from app.storage import SQLiteSessionStore


def test_sqlite_session_store_persists_turns() -> None:
    settings = Settings(database_url="sqlite:///:memory:")
    store = SQLiteSessionStore(settings)

    session = store.get_or_create("session-1")
    session.turns.extend(["User: hello", "Agent: hi"])
    store.save(session)

    reloaded = store.get_or_create("session-1")
    assert reloaded.turns == ["User: hello", "Agent: hi"]


def test_rate_limiter_blocks_after_limit() -> None:
    limiter = InMemoryRateLimiter(limit_per_minute=2)
    limiter.check("user-1")
    limiter.check("user-1")

    try:
        limiter.check("user-1")
    except Exception as exc:
        assert getattr(exc, "status_code") == 429
    else:
        raise AssertionError("Expected rate limiter to block the third request")
