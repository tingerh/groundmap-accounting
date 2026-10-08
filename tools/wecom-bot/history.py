from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class QueryLog:
    user_id: str
    chat_type: str
    question: str
    answer: str
    references: list[str]
    provider: str
    workspace: str
    input_tokens: int | None
    output_tokens: int | None
    status: str
    error: str | None
    duration_ms: int


class HistoryStore:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @staticmethod
    def user_key(user_id: str) -> str:
        return hashlib.sha256(user_id.encode("utf-8")).hexdigest()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialize(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_key TEXT NOT NULL,
                    chat_type TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    references_json TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    workspace TEXT NOT NULL,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    status TEXT NOT NULL,
                    error TEXT,
                    duration_ms INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_query_history_user_time "
                "ON query_history(user_key, created_at)"
            )
            conn.commit()

    def count_today(self, user_id: str) -> int:
        key = self.user_key(user_id)
        today = datetime.now().astimezone().date().isoformat()
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM query_history "
                "WHERE user_key = ? AND substr(created_at, 1, 10) = ? AND status = 'success'",
                (key, today),
            ).fetchone()
        return int(row[0]) if row else 0

    def add(self, item: QueryLog) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO query_history (
                    user_key, chat_type, question, answer, references_json,
                    provider, workspace, input_tokens, output_tokens,
                    status, error, duration_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.user_key(item.user_id),
                    item.chat_type,
                    item.question,
                    item.answer,
                    json.dumps(item.references, ensure_ascii=False),
                    item.provider,
                    item.workspace,
                    item.input_tokens,
                    item.output_tokens,
                    item.status,
                    item.error,
                    item.duration_ms,
                    datetime.now().astimezone().isoformat(timespec="seconds"),
                ),
            )
            conn.commit()
