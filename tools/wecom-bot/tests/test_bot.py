from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from config import load_settings
from groundmap_client import extract_final_answer, extract_references
from history import HistoryStore, QueryLog


class AnswerParsingTests(unittest.TestCase):
    def test_extracts_last_answer_section(self) -> None:
        text = "**【INTENT】分析**\n过程\n**【ANSWER】结论**\n最终内容"
        self.assertEqual(extract_final_answer(text), "最终内容")

    def test_deduplicates_references_and_builds_urls(self) -> None:
        text = (
            "结论 [[wiki/concepts/revenue#确认]] "
            "补充 [[wiki/concepts/revenue]] "
            "原文 [[raw/papers/cas14#^p-1-abc123]]"
        )
        refs = extract_references(text, "https://kb.example.com")
        self.assertEqual([r.target for r in refs], ["revenue", "cas14"])
        self.assertEqual(refs[0].url, "https://kb.example.com/page/wiki/concepts/revenue.md")


class HistoryTests(unittest.TestCase):
    def test_stores_hashed_user_and_counts_successes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = HistoryStore(Path(directory) / "history.db")
            store.add(
                QueryLog(
                    user_id="user-123",
                    chat_type="single",
                    question="q",
                    answer="a",
                    references=[],
                    provider="claude-code",
                    workspace="accounting-standards",
                    input_tokens=1,
                    output_tokens=2,
                    status="success",
                    error=None,
                    duration_ms=10,
                )
            )
            self.assertEqual(store.count_today("user-123"), 1)
            conn = store._connect()
            try:
                stored = conn.execute("SELECT user_key FROM query_history").fetchone()[0]
            finally:
                conn.close()
            self.assertNotEqual(stored, "user-123")


class ConfigTests(unittest.TestCase):
    def test_loads_an_explicit_enterprise_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "company-b.env"
            config.write_text(
                "\n".join(
                    [
                        "WECHAT_BOT_ID=company-b-bot",
                        "WECHAT_BOT_SECRET=company-b-secret",
                        "WECOM_ALLOWED_USER_IDS=user-b",
                        "WECOM_HISTORY_DB=data/company-b.db",
                        "GROUNDMAP_WORKSPACE=accounting-standards",
                    ]
                ),
                encoding="utf-8",
            )
            settings = load_settings(config)
            self.assertEqual(settings.bot_id, "company-b-bot")
            self.assertEqual(settings.allowed_user_ids, frozenset({"user-b"}))
            self.assertEqual(settings.history_db.name, "company-b.db")


if __name__ == "__main__":
    unittest.main()
