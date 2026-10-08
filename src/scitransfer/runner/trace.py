"""Append-only trace logging for paired runs. No secrets are recorded."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from ..core.types import StepRecord


class TraceLogger:
    """JSONL trace writer. One file per run directory."""

    def __init__(self, trace_path: Path | str):
        self.path = Path(trace_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            raise FileExistsError(f"Trace already exists: {self.path}")
        self.path.write_text("", encoding="utf-8")

    def append(self, record: StepRecord | dict[str, Any]) -> None:
        if isinstance(record, StepRecord):
            payload = record.to_dict()
        else:
            payload = dict(record)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
        return out


def write_run_result(run_dir: Path | str, result: dict[str, Any]) -> Path:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    out = run_dir / "run_result.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return out


def sanitize_secrets(text: str) -> str:
    """Best-effort redaction of common secret patterns before persisting."""
    import re

    text = re.sub(r"sk-[A-Za-z0-9]{8,}", "sk-***REDACTED***", text)
    text = re.sub(
        r"(?i)(api[_-]?key|token|secret|password)\s*[=:]\s*\S+",
        r"\1=***REDACTED***",
        text,
    )
    return text
