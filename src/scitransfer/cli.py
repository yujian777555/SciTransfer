"""SciTransfer CLI: audit, run-pair, summarize."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .benchmarks.scienceagentbench import (
    DEFAULT_PARQUET,
    check_evaluator_available,
    load_verified_tasks,
)
from .core.types import Arm, Budget, ScientificStrategy, stable_json
from .metrics import summarize_runs
from .runner.paired import run_pair


def cmd_audit(args: argparse.Namespace) -> int:
    tasks = load_verified_tasks(DEFAULT_PARQUET)
    domains: dict[str, int] = {}
    for t in tasks:
        domains[t.domain] = domains.get(t.domain, 0) + 1

    readiness = check_evaluator_available()
    report = {
        "benchmark": "ScienceAgentBench (verified split)",
        "upstream_repo": "https://github.com/OSU-NLP-Group/ScienceAgentBench",
        "upstream_head": args.upstream_head,
        "hf_dataset": "osunlp/ScienceAgentBench",
        "hf_dataset_sha": args.hf_sha,
        "n_tasks": len(tasks),
        "domain_counts": domains,
        "evaluator_readiness": readiness,
        "parquet_path": str(DEFAULT_PARQUET),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"written to {args.out}", file=sys.stderr)
    return 0


def cmd_run_pair(args: argparse.Namespace) -> int:
    budget = Budget(max_tokens=args.max_tokens, max_cost_usd=args.max_cost_usd, timeout_s=args.timeout)
    result = run_pair(
        instance_id=args.task_id,
        seed=args.seed,
        results_dir=args.results_dir,
        model=args.model,
        budget=budget,
        skip_evaluation=args.skip_evaluation,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    summary = summarize_runs(args.results_dir)
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    if args.out:
        Path(args.out).write_text(
            json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
        )
        print(f"written to {args.out}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="scitransfer", description="SciTransfer paired-strategy experiments")
    sub = parser.add_subparsers(dest="command", required=True)

    p_audit = sub.add_parser("audit", help="Inspect verified ScienceAgentBench and evaluator readiness")
    p_audit.add_argument("--upstream-head", default=None)
    p_audit.add_argument("--hf-sha", default=None)
    p_audit.add_argument("--out", default=None)
    p_audit.set_defaults(func=cmd_audit)

    p_run = sub.add_parser("run-pair", help="Run A/B pair on one task")
    p_run.add_argument("--task-id", type=int, required=True, help="ScienceAgentBench instance_id")
    p_run.add_argument("--seed", type=int, default=0)
    p_run.add_argument("--results-dir", default="results/round_001_runs")
    p_run.add_argument("--model", default="deepseek-v4-pro")
    p_run.add_argument("--max-tokens", type=int, default=32000)
    p_run.add_argument("--max-cost-usd", type=float, default=1.0)
    p_run.add_argument("--timeout", type=int, default=900)
    p_run.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Generate programs but do not invoke the official evaluator (records BLOCKED).",
    )
    p_run.set_defaults(func=cmd_run_pair)

    p_sum = sub.add_parser("summarize", help="Summarize runs under a results directory")
    p_sum.add_argument("--results-dir", default="results/round_001_runs")
    p_sum.add_argument("--out", default=None)
    p_sum.set_defaults(func=cmd_summarize)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
