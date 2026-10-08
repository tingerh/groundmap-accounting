from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.parse import quote

import aiohttp

from config import Settings


WIKI_REF_RE = re.compile(r"\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]")
ANSWER_RE = re.compile(r"\*\*【ANSWER】[^*]*\*\*", re.IGNORECASE)

@dataclass(frozen=True)
class Reference:
    target: str
    url: str | None


@dataclass(frozen=True)
class QueryResult:
    answer: str
    references: list[Reference]
    input_tokens: int | None
    output_tokens: int | None


def extract_final_answer(text: str) -> str:
    matches = list(ANSWER_RE.finditer(text))
    if not matches:
        return text.strip()
    return text[matches[-1].end() :].strip()


def extract_references(text: str, public_base_url: str) -> list[Reference]:
    found: list[Reference] = []
    seen: set[str] = set()
    for match in WIKI_REF_RE.finditer(text):
        raw = match.group(1).strip()
        path = raw.split("#", 1)[0]
        if not path or path in seen:
            continue
        seen.add(path)
        label = PurePosixPath(path).stem.replace("_", " ")
        url = None
        if public_base_url:
            md_path = path if path.endswith(".md") else f"{path}.md"
            url = f"{public_base_url}/page/{quote(md_path, safe='/')}"
        found.append(Reference(target=label, url=url))
    return found


class GroundMapClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def query(self, question: str) -> QueryResult:
        # Deliberately omit `system`: /api/chat applies the same default query
        # orchestration used by a fresh debug-console conversation. The bot is
        # only a presentation adapter and must not maintain a second retrieval path.
        payload = {
            "provider": self.settings.provider,
            "model": self.settings.model,
            "messages": [{"role": "user", "text": question}],
            "tool_budget": self.settings.tool_budget,
            "mode": self.settings.mode,
            "workspace": self.settings.workspace,
        }
        timeout = aiohttp.ClientTimeout(total=self.settings.query_timeout_seconds)
        answer_parts: list[str] = []
        usage: dict[str, int] = {}
        error: str | None = None

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(self.settings.chat_url, json=payload) as response:
                if response.status != 200:
                    detail = (await response.text())[:500]
                    raise RuntimeError(f"GroundMap returned HTTP {response.status}: {detail}")
                async for raw_line in response.content:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line.startswith("data:"):
                        continue
                    try:
                        event = json.loads(line[5:].strip())
                    except json.JSONDecodeError:
                        continue
                    kind = event.get("kind")
                    if kind == "text-delta" and isinstance(event.get("text"), str):
                        answer_parts.append(event["text"])
                    elif kind == "turn-end":
                        if isinstance(event.get("usage"), dict):
                            usage = event["usage"]
                        if event.get("reason") == "error":
                            error = str(event.get("error_message") or "query failed")

        if error:
            raise RuntimeError(error)
        full_text = "".join(answer_parts).strip()
        if not full_text:
            raise RuntimeError("GroundMap returned an empty answer")
        answer = extract_final_answer(full_text)
        references = extract_references(answer, self.settings.public_kb_base_url)
        return QueryResult(
            answer=answer,
            references=references,
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
        )


def format_wecom_reply(result: QueryResult, max_chars: int = 3500) -> str:
    body = result.answer
    if result.references:
        lines = ["", "**参考依据**"]
        for index, ref in enumerate(result.references[:5], 1):
            if ref.url:
                lines.append(f"{index}. [{ref.target}]({ref.url})")
            else:
                lines.append(f"{index}. {ref.target}")
        body += "\n" + "\n".join(lines)
    if len(body) > max_chars:
        body = body[: max_chars - 25].rstrip() + "\n\n（回答过长，已截断）"
    return body
