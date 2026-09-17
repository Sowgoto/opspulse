from __future__ import annotations

import re
from collections import Counter, defaultdict, deque
from datetime import datetime, timedelta

from .models import AnalysisResult, LogEvent, Signature


ERROR_LEVELS = {"ERROR", "CRITICAL"}


def normalize_signature(message: str) -> str:
    value = message.lower().strip()
    value = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<ip>", value)
    value = re.sub(r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b", "<uuid>", value, flags=re.I)
    value = re.sub(r"\b\d{5,}\b", "<id>", value)
    value = re.sub(r"\b(transaction_id|request_id|trace_id|pid)=[^\s]+", r"\1=<id>", value)
    value = re.sub(r"\s+", " ", value)
    return value[:180] or "(empty message)"


def _peak_error_window(events: list[LogEvent], minutes: int) -> tuple[datetime | None, int]:
    timestamps = sorted(event.timestamp for event in events if event.level in ERROR_LEVELS and event.timestamp)
    if not timestamps:
        return None, 0
    active: deque[datetime] = deque()
    best_start = timestamps[0]
    best_count = 0
    width = timedelta(minutes=minutes)
    for timestamp in timestamps:
        active.append(timestamp)
        while active and timestamp - active[0] >= width:
            active.popleft()
        if len(active) > best_count:
            best_count = len(active)
            best_start = active[0]
    return best_start, best_count


def _health_score(total: int, counts: Counter[str], spike: bool) -> int:
    if total == 0:
        return 100
    penalty = counts["WARNING"] * 2 + counts["ERROR"] * 6 + counts["CRITICAL"] * 15
    error_ratio = (counts["ERROR"] + counts["CRITICAL"]) / total
    penalty += round(error_ratio * 30)
    if spike:
        penalty += 10
    return max(0, min(100, 100 - penalty))


def _recommendations(counts: Counter[str], signatures: list[Signature], spike: bool) -> tuple[str, ...]:
    items: list[str] = []
    if spike:
        items.append("Correlate the peak window with deployments, infrastructure changes, and dependency alerts.")
    if signatures:
        top = signatures[0]
        services = ", ".join(top.services)
        items.append(f'Review the repeated signature "{top.text}" in service(s): {services}.')
    if counts["CRITICAL"]:
        items.append("Escalate critical events and verify customer-facing impact, failover, and recovery status.")
    if counts["ERROR"] or counts["CRITICAL"]:
        items.append("Check upstream dependencies, resource saturation, recent releases, and network connectivity.")
    if counts["WARNING"]:
        items.append("Track warnings for capacity or degradation signals before closing the incident.")
    if not items:
        items.append("No immediate error indicators found; continue normal monitoring.")
    return tuple(items)


def analyze(events: list[LogEvent], window_minutes: int = 5, spike_threshold: int = 5) -> AnalysisResult:
    level_counts: Counter[str] = Counter(event.level for event in events)
    service_counts: Counter[str] = Counter(event.service for event in events)

    grouped: Counter[str] = Counter()
    grouped_services: dict[str, set[str]] = defaultdict(set)
    for event in events:
        if event.level in ERROR_LEVELS:
            signature = normalize_signature(event.message)
            grouped[signature] += 1
            grouped_services[signature].add(event.service)

    top_signatures = [
        Signature(text=text, count=count, services=tuple(sorted(grouped_services[text])))
        for text, count in grouped.most_common(5)
    ]
    peak_start, peak_count = _peak_error_window(events, window_minutes)
    spike = peak_count >= spike_threshold
    score = _health_score(len(events), level_counts, spike)
    status = "HEALTHY" if score >= 80 else "DEGRADED" if score >= 50 else "CRITICAL"

    return AnalysisResult(
        total_events=len(events),
        level_counts={level: level_counts[level] for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")},
        service_counts=dict(service_counts.most_common()),
        top_signatures=tuple(top_signatures),
        peak_window_start=peak_start,
        peak_window_errors=peak_count,
        spike_detected=spike,
        health_score=score,
        status=status,
        recommendations=_recommendations(level_counts, top_signatures, spike),
    )
