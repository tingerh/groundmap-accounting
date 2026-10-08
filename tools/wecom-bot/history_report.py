from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def read_database(path: Path, limit: int) -> list[dict[str, object]]:
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """
            SELECT id, user_key, chat_type, question, answer, references_json,
                   provider, workspace, input_tokens, output_tokens, status,
                   error, duration_ms, created_at
            FROM query_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    finally:
        connection.close()

    result: list[dict[str, object]] = []
    for row in rows:
        try:
            references = json.loads(row["references_json"])
        except (TypeError, json.JSONDecodeError):
            references = []
        result.append(
            {
                "id": row["id"],
                "database": path.stem,
                "user_key": row["user_key"][:8],
                "chat_type": row["chat_type"],
                "question": row["question"],
                "answer": row["answer"],
                "references": references,
                "provider": row["provider"],
                "workspace": row["workspace"],
                "input_tokens": row["input_tokens"],
                "output_tokens": row["output_tokens"],
                "status": row["status"],
                "error": row["error"],
                "duration_ms": row["duration_ms"],
                "created_at": row["created_at"],
            }
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Read enterprise WeChat bot history")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()

    records: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    for database in sorted(args.data_dir.glob("*.db")):
        try:
            records.extend(read_database(database, max(1, min(args.limit, 2000))))
        except (sqlite3.Error, OSError) as exc:
            errors.append({"database": database.name, "error": str(exc)})
    records.sort(key=lambda item: str(item["created_at"]), reverse=True)
    payload = json.dumps({"records": records, "errors": errors}, ensure_ascii=False)
    sys.stdout.buffer.write(payload.encode("utf-8"))


if __name__ == "__main__":
    main()
