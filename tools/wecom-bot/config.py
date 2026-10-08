from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


@dataclass(frozen=True)
class Settings:
    bot_id: str
    bot_secret: str
    allowed_user_ids: frozenset[str]
    chat_url: str
    provider: str
    model: str
    workspace: str
    mode: str
    tool_budget: int
    query_timeout_seconds: int
    public_kb_base_url: str
    daily_query_limit: int
    max_question_chars: int
    history_db: Path

    def user_is_allowed(self, user_id: str) -> bool:
        return "*" in self.allowed_user_ids or user_id in self.allowed_user_ids


def load_settings(config_path: Path | str | None = None) -> Settings:
    source = Path(config_path) if config_path else ROOT / ".env.local"
    if not source.is_absolute():
        source = (Path.cwd() / source).resolve()
    if not source.is_file():
        raise ValueError(f"Configuration file does not exist: {source}")
    load_dotenv(source, override=True)
    bot_id = os.getenv("WECHAT_BOT_ID", "").strip()
    bot_secret = os.getenv("WECHAT_BOT_SECRET", "").strip()
    if not bot_id or not bot_secret:
        raise ValueError(f"WECHAT_BOT_ID and WECHAT_BOT_SECRET are required in {source}")

    allowed = frozenset(
        item.strip()
        for item in os.getenv("WECOM_ALLOWED_USER_IDS", "").split(",")
        if item.strip()
    )
    history = Path(os.getenv("WECOM_HISTORY_DB", "data/query-history.db"))
    if not history.is_absolute():
        history = ROOT / history

    return Settings(
        bot_id=bot_id,
        bot_secret=bot_secret,
        allowed_user_ids=allowed,
        chat_url=os.getenv("GROUNDMAP_CHAT_URL", "http://localhost:3100/api/chat").strip(),
        provider=os.getenv("GROUNDMAP_PROVIDER", "claude-code").strip(),
        model=os.getenv("GROUNDMAP_MODEL", "default").strip(),
        workspace=os.getenv("GROUNDMAP_WORKSPACE", "accounting-standards").strip(),
        mode=os.getenv("GROUNDMAP_MODE", "quick").strip(),
        tool_budget=_int_env("GROUNDMAP_TOOL_BUDGET", 10),
        query_timeout_seconds=_int_env("GROUNDMAP_QUERY_TIMEOUT_SECONDS", 240),
        public_kb_base_url=os.getenv("PUBLIC_KB_BASE_URL", "").strip().rstrip("/"),
        daily_query_limit=_int_env("WECOM_DAILY_QUERY_LIMIT", 10),
        max_question_chars=_int_env("WECOM_MAX_QUESTION_CHARS", 2000),
        history_db=history,
    )
