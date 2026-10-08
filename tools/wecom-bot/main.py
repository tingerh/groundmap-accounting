from __future__ import annotations

import asyncio
import argparse
import logging
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from aibot import WSClient, WSClientOptions, generate_req_id

from config import load_settings
from groundmap_client import GroundMapClient, format_wecom_reply
from history import HistoryStore, QueryLog


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
LOGGER = logging.getLogger("groundmap-wecom")


def _sender_id(frame: dict[str, Any]) -> str:
    body = frame.get("body") or {}
    sender = body.get("from") or body.get("sender") or {}
    if isinstance(sender, dict):
        value = sender.get("userid") or sender.get("user_id")
        if value:
            return str(value)
    return str(body.get("userid") or body.get("user_id") or "")


def _chat_type(frame: dict[str, Any]) -> str:
    body = frame.get("body") or {}
    return str(body.get("chattype") or body.get("chat_type") or "single")


def _question(frame: dict[str, Any]) -> str:
    body = frame.get("body") or {}
    text = body.get("text") or {}
    return str(text.get("content") or "").strip() if isinstance(text, dict) else ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GroundMap enterprise WeChat bot")
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to an enterprise-specific .env file (default: .env.local)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the selected configuration without connecting to enterprise WeChat",
    )
    return parser.parse_args()


async def run(config_path: Path | None = None) -> None:
    settings = load_settings(config_path)
    history = HistoryStore(settings.history_db)
    groundmap = GroundMapClient(settings)
    user_locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
    client = WSClient(
        WSClientOptions(
            bot_id=settings.bot_id,
            secret=settings.bot_secret,
            max_reconnect_attempts=-1,
        )
    )

    @client.on("authenticated")
    def on_authenticated() -> None:
        LOGGER.info("Enterprise WeChat bot authenticated")

    @client.on("disconnected")
    def on_disconnected(reason: str) -> None:
        LOGGER.warning("Enterprise WeChat bot disconnected: %s", reason)

    @client.on("error")
    def on_error(error: Exception) -> None:
        LOGGER.error("Enterprise WeChat bot error: %s", error)

    @client.on("event.enter_chat")
    async def on_enter_chat(frame: dict[str, Any]) -> None:
        await client.reply_welcome(
            frame,
            {
                "msgtype": "text",
                "text": {
                    "content": "您好，我是 GroundMap 知识助手。请输入需要查询的专业问题。"
                },
            },
        )

    @client.on("message.text")
    async def on_text(frame: dict[str, Any]) -> None:
        user_id = _sender_id(frame)
        question = _question(frame)
        chat_type = _chat_type(frame)
        stream_id = generate_req_id("groundmap")

        if not user_id:
            LOGGER.warning("Message ignored because no user ID was present; body keys=%s", list((frame.get("body") or {}).keys()))
            await client.reply_stream(frame, stream_id, "无法识别用户身份，请联系管理员。", True)
            return
        if question.lower() == "/whoami":
            await client.reply_stream(
                frame,
                stream_id,
                f"你的企业微信 User ID：`{user_id}`\n\n请仅将该标识提供给机器人管理员。",
                True,
            )
            return
        if not settings.user_is_allowed(user_id):
            await client.reply_stream(
                frame,
                stream_id,
                "当前账号不在测试白名单中。发送 `/whoami` 可查看自己的 User ID。",
                True,
            )
            return
        if not question:
            await client.reply_stream(frame, stream_id, "请输入文本问题。", True)
            return
        if len(question) > settings.max_question_chars:
            await client.reply_stream(
                frame,
                stream_id,
                f"问题过长，请控制在 {settings.max_question_chars} 个字符以内。",
                True,
            )
            return
        if history.count_today(user_id) >= settings.daily_query_limit:
            await client.reply_stream(
                frame,
                stream_id,
                f"今天的测试额度已用完（每人 {settings.daily_query_limit} 次）。",
                True,
            )
            return

        lock = user_locks[user_id]
        if lock.locked():
            await client.reply_stream(frame, stream_id, "上一条问题仍在处理中，请稍后再试。", True)
            return

        async with lock:
            await client.reply_stream(frame, stream_id, "正在查询 GroundMap 知识库…", False)
            started = time.perf_counter()
            try:
                result = await groundmap.query(question)
                reply = format_wecom_reply(result)
                await client.reply_stream(frame, stream_id, reply, True)
                history.add(
                    QueryLog(
                        user_id=user_id,
                        chat_type=chat_type,
                        question=question,
                        answer=result.answer,
                        references=[ref.target for ref in result.references],
                        provider=settings.provider,
                        workspace=settings.workspace,
                        input_tokens=result.input_tokens,
                        output_tokens=result.output_tokens,
                        status="success",
                        error=None,
                        duration_ms=int((time.perf_counter() - started) * 1000),
                    )
                )
            except Exception as exc:
                LOGGER.exception("GroundMap query failed")
                error_text = str(exc)
                if "timeout" in error_text.lower():
                    message = "查询超时，知识库未能在规定时间内完成回答，请稍后重试。"
                elif "启动失败" in error_text or "ENOENT" in error_text:
                    message = "查询服务未能启动回答程序，请联系管理员检查模型配置。"
                else:
                    message = "查询失败，原因已记录在本机日志中，请联系管理员检查。"
                await client.reply_stream(frame, stream_id, message, True)
                history.add(
                    QueryLog(
                        user_id=user_id,
                        chat_type=chat_type,
                        question=question,
                        answer="",
                        references=[],
                        provider=settings.provider,
                        workspace=settings.workspace,
                        input_tokens=None,
                        output_tokens=None,
                        status="error",
                        error=str(exc)[:1000],
                        duration_ms=int((time.perf_counter() - started) * 1000),
                    )
                )

    if not settings.allowed_user_ids:
        LOGGER.warning("WECOM_ALLOWED_USER_IDS is empty; all query messages will be denied")
    LOGGER.info("Starting GroundMap enterprise WeChat bot for workspace=%s", settings.workspace)
    await client.connect()
    await asyncio.Event().wait()


if __name__ == "__main__":
    args = parse_args()
    if args.check:
        checked = load_settings(args.config)
        print(
            "Configuration OK: "
            f"workspace={checked.workspace}, provider={checked.provider}, "
            f"history_db={checked.history_db}"
        )
    else:
        asyncio.run(run(args.config))
