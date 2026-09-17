from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone

from .models import AnalysisResult


def _timestamp(value: datetime | None) -> str | None:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if value else None


def to_dict(result: AnalysisResult) -> dict[str, object]:
    payload = asdict(result)
    payload["peak_window_start"] = _timestamp(result.peak_window_start)
    payload["generated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return payload


def render_json(result: AnalysisResult) -> str:
    return json.dumps(to_dict(result), indent=2) + "\n"


def render_markdown(result: AnalysisResult, source: str, window_minutes: int) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    peak = _timestamp(result.peak_window_start) or "N/A"
    lines = [
        "# OpsPulse Incident Analysis",
        "",
        f"- **Source:** `{source}`",
        f"- **Generated:** {generated}",
        f"- **Status:** **{result.status}**",
        f"- **Health score:** **{result.health_score}/100**",
        "",
        "## Executive summary",
        "",
        f"Analyzed **{result.total_events} events**. Detected **{result.level_counts['ERROR']} errors**, "
        f"**{result.level_counts['CRITICAL']} critical events**, and **{result.level_counts['WARNING']} warnings**.",
        "",
        "## Severity distribution",
        "",
        "| Level | Count |",
        "|---|---:|",
    ]
    for level, count in result.level_counts.items():
        lines.append(f"| {level} | {count} |")

    lines.extend([
        "",
        "## Spike detection",
        "",
        f"- Window: {window_minutes} minutes",
        f"- Peak window start: {peak}",
        f"- Errors in peak window: {result.peak_window_errors}",
        f"- Spike detected: {'Yes' if result.spike_detected else 'No'}",
        "",
        "## Top error signatures",
        "",
    ])
    if result.top_signatures:
        lines.extend(["| Count | Services | Normalized signature |", "|---:|---|---|"])
        for item in result.top_signatures:
            services = ", ".join(item.services)
            signature = item.text.replace("|", "\\|")
            lines.append(f"| {item.count} | {services} | `{signature}` |")
    else:
        lines.append("No error signatures detected.")

    lines.extend(["", "## Recommended next actions", ""])
    lines.extend(f"{index}. {item}" for index, item in enumerate(result.recommendations, start=1))
    lines.extend(["", "---", "Generated locally by OpsPulse. Review for sensitive data before sharing.", ""])
    return "\n".join(lines)

