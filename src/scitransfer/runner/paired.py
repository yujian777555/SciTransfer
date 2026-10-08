"""Paired A/B execution on identical task and initial environment.

A = NO_STRATEGY, B = FIXED_STRATEGY (preregistered).
Each arm runs into its own directory with its own trace.
"""
from __future__ import annotations

import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ..agent import FIXED_STRATEGY, build_prompt, call_deepseek
from ..benchmarks.scienceagentbench import (
    DEFAULT_BENCHMARK_DIR,
    DEFAULT_PARQUET,
    DEFAULT_UPSTREAM_DIR,
    PINNED_SPLIT,
    EvaluatorUnavailable,
    OfficialEvalResult,
    TaskMeta,
    check_evaluator_available,
    get_task,
    run_official_evaluation,
)
from ..core.types import (
    Arm,
    Budget,
    RunResult,
    ScientificStrategy,
    sha256_of,
    stable_json,
)
from .trace import TraceLogger, sanitize_secrets, write_run_result


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def environment_fingerprint() -> str:
    payload = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
    }
    return sha256_of(stable_json(payload))[:16]


def run_single_arm(
    task: TaskMeta,
    arm: Arm,
    seed: int,
    results_dir: Path | str,
    model: str = "deepseek-v4-pro",
    strategy: Optional[ScientificStrategy] = None,
    budget: Optional[Budget] = None,
    dataset_path: str = "benchmark/datasets",
    skip_evaluation: bool = False,
) -> RunResult:
    """Execute one arm on one task. Fail-closed on evaluator absence when evaluation requested."""
    budget = budget or Budget()
    results_dir = Path(results_dir)
    run_dir = results_dir / f"{task.task_key}__{arm.value}__seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)

    started = _now()
    env_sha = environment_fingerprint()
    prompt, strategy_id, strategy_hash = build_prompt(task.to_dict(), arm, strategy, dataset_path)
    prompt_hash = sha256_of(prompt)

    # Persist the exact prompt for audit.
    (run_dir / "prompt.txt").write_text(sanitize_secrets(prompt), encoding="utf-8")
    if strategy_id:
        (run_dir / "strategy.json").write_text(
            json.dumps((strategy or FIXED_STRATEGY).to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    trace = TraceLogger(run_dir / "trace.jsonl")
    trace.append(
        {
            "event": "run_start",
            "timestamp": started,
            "task_id": task.task_key,
            "instance_id": task.instance_id,
            "domain": task.domain,
            "arm": arm.value,
            "seed": seed,
            "agent_id": "scitransfer-direct-prompt",
            "agent_model": model,
            "environment_sha": env_sha,
            "prompt_hash": prompt_hash,
            "strategy_id": strategy_id,
            "strategy_hash": strategy_hash,
            "budget": budget.to_dict(),
        }
    )

    # ---- Agent generation ----
    t_gen0 = time.time()
    resp = call_deepseek(
        prompt,
        model=model,
        max_tokens=min(budget.max_tokens, 8192),
        temperature=0.0,
    )
    t_gen1 = time.time()

    # Override strategy fields from build_prompt (call_deepseek leaves them None).
    resp.strategy_id = strategy_id
    resp.strategy_hash = strategy_hash

    raw_path = run_dir / "agent_raw_response.txt"
    raw_path.write_text(sanitize_secrets(resp.text or (resp.error or "")), encoding="utf-8")

    if resp.error and not resp.program:
        trace.append(
            {
                "event": "agent_error",
                "timestamp": _now(),
                "error": resp.error,
                "tokens_in": resp.tokens_in,
                "tokens_out": resp.tokens_out,
                "cost_usd": resp.cost_usd,
                "duration_s": round(t_gen1 - t_gen0, 3),
            }
        )
        result = RunResult(
            task_id=task.task_key,
            domain=task.domain,
            arm=arm.value,
            seed=seed,
            agent_id="scitransfer-direct-prompt",
            agent_model=model,
            status="ERROR",
            score=None,
            official_evaluation=False,
            cost_usd=resp.cost_usd,
            tokens_in=resp.tokens_in,
            tokens_out=resp.tokens_out,
            prompt_hash=prompt_hash,
            strategy_id=strategy_id,
            strategy_hash=strategy_hash,
            environment_sha=env_sha,
            trace_path=str(trace.path),
            evaluator_output_path=None,
            error=resp.error,
            exit_reason="agent_error",
            started_at=started,
            finished_at=_now(),
            extra={
                "instance_id": task.instance_id,
                "prompt_path": str(run_dir / "prompt.txt"),
            },
        )
        write_run_result(run_dir, result.to_dict())
        return result

    # Save generated program in official naming convention.
    pred_name = "pred_" + task.gold_program_name
    pred_path = run_dir / pred_name
    pred_path.write_text(resp.program or "", encoding="utf-8")

    trace.append(
        {
            "event": "agent_response",
            "timestamp": _now(),
            "program_path": str(pred_path),
            "program_sha256": sha256_of(resp.program or ""),
            "tokens_in": resp.tokens_in,
            "tokens_out": resp.tokens_out,
            "cost_usd": resp.cost_usd,
            "duration_s": round(t_gen1 - t_gen0, 3),
            "raw_response_path": str(raw_path),
        }
    )

    # ---- Official evaluation (R1: pinned split, absolute paths, row-index parsing) ----
    eval_result: Optional[OfficialEvalResult] = None
    status = "SUCCESS"
    score: Optional[float] = None
    official = False
    eval_out_path: Optional[str] = None
    error: Optional[str] = None
    exit_reason = "completed"

    if skip_evaluation:
        exit_reason = "evaluation_skipped_by_config"
        status = "BLOCKED"
        error = "Evaluation skipped by configuration; no official score claimed."
    else:
        try:
            eval_result = run_official_evaluation(
                task=task,
                pred_program_path=run_dir,
                benchmark_dir=DEFAULT_BENCHMARK_DIR,
                upstream_dir=DEFAULT_UPSTREAM_DIR,
                output_dir=run_dir,
                run_id=f"r1_{arm.value}_s{seed}_i{task.instance_id}",
                parquet_path=DEFAULT_PARQUET,
                split=PINNED_SPLIT,
            )
            official = eval_result.official_evaluation
            eval_out_path = eval_result.raw_output_path
            if not official:
                # Fail-closed: any invariant failure → BLOCKED or ERROR, score stays None.
                err = eval_result.error or "Unknown evaluator failure"
                if "Unavailable" in err or "not runnable" in err:
                    status = "BLOCKED"
                elif eval_result.is_placeholder:
                    status = "BLOCKED"
                else:
                    status = "ERROR"
                error = err
                exit_reason = "official_eval_invariant_failed"
            else:
                # success_rate is the official 0/1 task score.
                score = float(eval_result.success_rate) if eval_result.success_rate is not None else None
                if score is None:
                    status = "ERROR"
                    error = "official_evaluation=True but score is None (internal error)"
                    exit_reason = "official_eval_invariant_failed"
                else:
                    status = "SUCCESS" if score == 1.0 else "FAILED"
                    exit_reason = "official_evaluated"
        except EvaluatorUnavailable as e:
            status = "BLOCKED"
            official = False
            score = None
            error = str(e)
            exit_reason = "official_evaluator_unavailable"
            eval_out_path = None

    trace.append(
        {
            "event": "run_end",
            "timestamp": _now(),
            "status": status,
            "official_evaluation": official,
            "score": score,
            "evaluator_output_path": eval_out_path,
            "error": sanitize_secrets(error) if error else None,
            "exit_reason": exit_reason,
            "eval_detail": eval_result.to_dict() if eval_result else None,
        }
    )

    result = RunResult(
        task_id=task.task_key,
        domain=task.domain,
        arm=arm.value,
        seed=seed,
        agent_id="scitransfer-direct-prompt",
        agent_model=model,
        status=status,
        score=score,
        official_evaluation=official,
        cost_usd=resp.cost_usd,
        tokens_in=resp.tokens_in,
        tokens_out=resp.tokens_out,
        prompt_hash=prompt_hash,
        strategy_id=strategy_id,
        strategy_hash=strategy_hash,
        environment_sha=env_sha,
        trace_path=str(trace.path),
        evaluator_output_path=eval_out_path,
        error=sanitize_secrets(error) if error else None,
        exit_reason=exit_reason,
        started_at=started,
        finished_at=_now(),
        extra={
            "instance_id": task.instance_id,
            "pred_program": str(pred_path),
            "prompt_path": str(run_dir / "prompt.txt"),
        },
    )
    write_run_result(run_dir, result.to_dict())
    return result


def run_pair(
    instance_id: int,
    seed: int,
    results_dir: Path | str,
    model: str = "deepseek-v4-pro",
    strategy: Optional[ScientificStrategy] = None,
    parquet_path: Path | str = DEFAULT_PARQUET,
    budget: Optional[Budget] = None,
    dataset_path: str = "benchmark/datasets",
    skip_evaluation: bool = False,
) -> dict[str, Any]:
    """Run A (no strategy) and B (fixed strategy) on the same task and seed."""
    task = get_task(instance_id, parquet_path)
    results_dir = Path(results_dir)

    # Record evaluator readiness once per pair.
    readiness = check_evaluator_available()
    (results_dir / f"{task.task_key}__seed{seed}__evaluator_readiness.json").write_text(
        json.dumps(readiness, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    run_a = run_single_arm(
        task, Arm.NO_STRATEGY, seed, results_dir,
        model=model, budget=budget, dataset_path=dataset_path,
        skip_evaluation=skip_evaluation,
    )
    run_b = run_single_arm(
        task, Arm.FIXED_STRATEGY, seed, results_dir,
        model=model, strategy=strategy, budget=budget, dataset_path=dataset_path,
        skip_evaluation=skip_evaluation,
    )

    pair_dir = results_dir / f"{task.task_key}__seed{seed}"
    pair_dir.mkdir(parents=True, exist_ok=True)
    pair = {
        "task_id": task.task_key,
        "instance_id": task.instance_id,
        "domain": task.domain,
        "seed": seed,
        "model": model,
        "evaluator_readiness": readiness,
        "arm_a": run_a.to_dict(),
        "arm_b": run_b.to_dict(),
        "paired_score_difference": (
            (run_b.score - run_a.score)
            if run_a.score is not None and run_b.score is not None
            else None
        ),
        "paired_cost_difference_usd": (
            (run_b.cost_usd or 0) - (run_a.cost_usd or 0)
        ),
    }
    (pair_dir / "pair_result.json").write_text(
        json.dumps(pair, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    return pair
