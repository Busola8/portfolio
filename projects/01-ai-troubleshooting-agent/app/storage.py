from __future__ import annotations

import sqlite3
import logging
from pathlib import Path

from .models import SessionState
from .settings import DATA_DIR, Settings

logger = logging.getLogger("troubleshooting-agent.storage")


class SessionStore:
    def get_or_create(self, session_id: str) -> SessionState:
        raise NotImplementedError

    def save(self, session: SessionState) -> None:
        raise NotImplementedError


class SQLiteSessionStore(SessionStore):
    def __init__(self, settings: Settings) -> None:
        db_path = self._resolve_path(settings.database_url)
        self.memory_connection: sqlite3.Connection | None = None
        if str(db_path) != ":memory:":
            db_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            self.memory_connection = sqlite3.connect(":memory:", check_same_thread=False)
        self.db_path = db_path
        try:
            self._initialize()
        except sqlite3.OperationalError as exc:
            self._fallback_to_memory(exc)

    @staticmethod
    def _resolve_path(database_url: str) -> Path:
        if database_url.startswith("sqlite:///"):
            raw_path = database_url.replace("sqlite:///", "", 1)
            if raw_path == ":memory:":
                return Path(":memory:")
            return Path(raw_path)
        return DATA_DIR / "sessions.db"

    def _connect(self) -> sqlite3.Connection:
        if self.memory_connection is not None:
            return self.memory_connection
        return sqlite3.connect(self.db_path)

    def _fallback_to_memory(self, exc: sqlite3.OperationalError) -> None:
        logger.warning("Falling back to in-memory sessions: %s", exc)
        self.db_path = Path(":memory:")
        self.memory_connection = sqlite3.connect(":memory:", check_same_thread=False)
        self._initialize()

    def _initialize(self) -> None:
        connection = self._connect()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                turns TEXT NOT NULL DEFAULT ''
            )
            """
        )
        connection.commit()

    def get_or_create(self, session_id: str) -> SessionState:
        try:
            connection = self._connect()
            row = connection.execute(
                "SELECT turns FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if row is None:
                connection.execute(
                    "INSERT INTO sessions (session_id, turns) VALUES (?, '')",
                    (session_id,),
                )
                connection.commit()
                return SessionState(session_id=session_id)
        except sqlite3.OperationalError as exc:
            self._fallback_to_memory(exc)
            connection = self._connect()
            connection.execute(
                "INSERT INTO sessions (session_id, turns) VALUES (?, '')",
                (session_id,),
            )
            connection.commit()
            return SessionState(session_id=session_id)
        turns = [turn for turn in row[0].split("\n") if turn]
        return SessionState(session_id=session_id, turns=turns)

    def save(self, session: SessionState) -> None:
        turns = "\n".join(session.turns[-8:])
        try:
            connection = self._connect()
            connection.execute(
                """
                INSERT INTO sessions (session_id, turns)
                VALUES (?, ?)
                ON CONFLICT(session_id) DO UPDATE SET turns = excluded.turns
                """,
                (session.session_id, turns),
            )
            connection.commit()
        except sqlite3.OperationalError as exc:
            self._fallback_to_memory(exc)
            connection = self._connect()
            connection.execute(
                """
                INSERT INTO sessions (session_id, turns)
                VALUES (?, ?)
                ON CONFLICT(session_id) DO UPDATE SET turns = excluded.turns
                """,
                (session.session_id, turns),
            )
            connection.commit()
