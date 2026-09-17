from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class LogEvent:
    timestamp: datetime | None
    level: str
    service: str
    message: str
    raw: str


@dataclass(frozen=True)
class Signature:
    text: str
    count: int
    services: tuple[str, ...]


@dataclass(frozen=True)
class AnalysisResult:
    total_events: int
    level_counts: dict[str, int]
    service_counts: dict[str, int]
    top_signatures: tuple[Signature, ...]
    peak_window_start: datetime | None
    peak_window_errors: int
    spike_detected: bool
    health_score: int
    status: str
    recommendations: tuple[str, ...] = field(default_factory=tuple)

