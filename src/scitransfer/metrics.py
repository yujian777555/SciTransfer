"""Parse official scores and compute paired differences. No significance claims on tiny pilots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from .core.types import stable_json


def parse_official_score(eval_dict: dict[str, Any]) -> Optional[float]:
    """Extract the official task success score (0/1) from an evaluator record.

    Returns None when the record does not represent a genuine official evaluation.
    """
    if not eval_dict.get("official_evaluation", False):
        return None
    sr = eval_dict.get("success_rate")
    if sr is None:
        return None
    return float(sr)


def summarize_runs(results_dir: Path | str) -> dict[str, Any]:
    """Walk results_dir, collect run_result.json and pair_result.json, build a summary."""
    root = Path(results_dir)
    runs: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []

    for p in sorted(root.rglob("run_result.json")):
        try:
            runs.append(json.loads(p.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    for p in sorted(root.rglob("pair_result.json")):
        try:
            pairs.append(json.loads(p.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue

    by_domain: dict[str, list[dict[str, Any]]] = {}
    for r in runs:
        by_domain.setdefault(r.get("domain", "unknown"), []).append(r)

    domain_summary: dict[str, Any] = {}
    for dom, rs in by_domain.items():
        domain_summary[dom] = {
            "n_runs": len(rs),
            "n_official": sum(1 for r in rs if r.get("official_evaluation")),
            "scores": [
                {"task_id": r["task_id"], "arm": r["arm"], "seed": r.get("seed"),
                 "score": r.get("score"), "status": r.get("status")}
                for r in rs
            ],
            "total_cost_usd": round(sum(r.get("cost_usd") or 0 for r in rs), 6),
        }

    n_paired_official = sum(
        1
        for p in pairs
        if p.get("arm_a", {}).get("official_evaluation")
        and p.get("arm_b", {}).get("official_evaluation")
    )

    return {
        "results_dir": str(root),
        "n_runs": len(runs),
        "n_pairs": len(pairs),
        "n_pairs_with_official_eval_both_arms": n_paired_official,
        "domains": domain_summary,
        "pairs": [
            {
                "task_id": p.get("task_id"),
                "domain": p.get("domain"),
                "seed": p.get("seed"),
                "score_a": p.get("arm_a", {}).get("score"),
                "score_b": p.get("arm_b", {}).get("score"),
                "diff": p.get("paired_score_difference"),
                "cost_a": p.get("arm_a", {}).get("cost_usd"),
                "cost_b": p.get("arm_b", {}).get("cost_usd"),
            }
            for p in pairs
        ],
    }


def paired_difference(score_b: Optional[float], score_a: Optional[float]) -> Optional[float]:
    if score_a is None or score_b is None:
        return None
    return score_b - score_a
