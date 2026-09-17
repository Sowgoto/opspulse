from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .models import LogEvent


LEVELS = {"DEBUG", "INFO", "NOTICE", "WARNING", "WARN", "ERROR", "CRITICAL", "CRIT", "FATAL"}
LEVEL_ALIASES = {"WARN": "WARNING", "NOTICE": "INFO", "CRIT": "CRITICAL", "FATAL": "CRITICAL"}

PLAIN_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[T ][0-9:.+-]+Z?)\s+"
    r"(?P<level>DEBUG|INFO|NOTICE|WARNING|WARN|ERROR|CRITICAL|CRIT|FATAL)\s+"
    r"(?:(?P<service>[A-Za-z0-9_.-]+)\s+)?(?P<message>.*)$",
    re.IGNORECASE,
)


def parse_timestamp(value: object) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def normalize_level(value: object) -> str:
    level = str(value or "INFO").upper()
    level = LEVEL_ALIASES.get(level, level)
    return level if level in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"} else "INFO"


def parse_line(line: str) -> LogEvent:
    raw = line.rstrip("\n")
    stripped = raw.strip()
    if not stripped:
        return LogEvent(None, "INFO", "unknown", "", raw)

    if stripped.startswith("{"):
        try:
            item = json.loads(stripped)
            if isinstance(item, dict):
                return LogEvent(
                    timestamp=parse_timestamp(item.get("timestamp") or item.get("time") or item.get("@timestamp")),
                    level=normalize_level(item.get("level") or item.get("severity")),
                    service=str(item.get("service") or item.get("application") or "unknown"),
                    message=str(item.get("message") or item.get("msg") or stripped),
                    raw=raw,
                )
        except json.JSONDecodeError:
            pass

    match = PLAIN_PATTERN.match(stripped)
    if match:
        values = match.groupdict()
        return LogEvent(
            timestamp=parse_timestamp(values["timestamp"]),
            level=normalize_level(values["level"]),
            service=values.get("service") or "unknown",
            message=values.get("message") or "",
            raw=raw,
        )

    discovered = next((level for level in LEVELS if re.search(rf"\b{level}\b", stripped, re.I)), "INFO")
    return LogEvent(None, normalize_level(discovered), "unknown", stripped, raw)


def parse_file(path: Path) -> list[LogEvent]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return [parse_line(line) for line in handle if line.strip()]

