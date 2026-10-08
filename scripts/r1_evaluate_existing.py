"""R1 evaluation runner: score existing Round 001 programs with official evaluator.

Retrospective scoring only — does NOT generate new programs.
Each program is scored independently with a distinct run_id.
Results are stored in results/round_001_r1_runs/.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.benchmarks.scienceagentbench import (
    DEFAULT_BENCHMARK_DIR,
    DEFAULT_PARQUET,
    DEFAULT_UPSTREAM_DIR,
    PINNED_SPLIT,
    EvaluatorUnavailable,
    check_evaluator_available,
    get_task,
    get_row_index_map,
    run_official_evaluation,
)

# The 6 existing Round 001 programs (task, arm, run_dir_name)
TARGETS = [
    {"instance_id": 85, "arm": "NO_STRATEGY", "run_dir": "sab_verified_85__NO_STRATEGY__seed0"},
    {"instance_id": 85, "arm": "FIXED_STRATEGY", "run_dir": "sab_verified_85__FIXED_STRATEGY__seed0"},
    {"instance_id": 16, "arm": "NO_STRATEGY", "run_dir": "sab_verified_16__NO_STRATEGY__seed0"},
    {"instance_id": 16, "arm": "FIXED_STRATEGY", "run_dir": "sab_verified_16__FIXED_STRATEGY__seed0"},
    {"instance_id": 21, "arm": "NO_STRATEGY", "run_dir": "sab_verified_21__NO_STRATEGY__seed0"},
    {"instance_id": 21, "arm": "FIXED_STRATEGY", "run_dir": "sab_verified_21__FIXED_STRATEGY__seed0"},
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    readiness = check_evaluator_available()
    print("Evaluator readiness:", json.dumps(readiness, indent=2))

    if not readiness["ready"]:
        print("BLOCKED: evaluator artifacts not ready. Cannot score.")
        missing = [k for k, v in readiness.items() if v is False and k != "ready"]
        print(f"Missing: {missing}")
        sys.exit(1)

    row_map = get_row_index_map()
    results = []
    out_root = Path("results/round_001_r1_runs")
    out_root.mkdir(parents=True, exist_ok=True)

    for t in TARGETS:
        instance_id = t["instance_id"]
        arm = t["arm"]
        run_dir = Path("results/round_001_runs") / t["run_dir"]

        # Find the pred_* program in the run directory
        pred_files = list(run_dir.glob("pred_*.py"))
        if not pred_files:
            print(f"SKIP {t['run_dir']}: no pred_*.py found")
            continue
        pred_file = pred_files[0]
        program_hash = sha256_file(pred_file)

        # Create a pred_programs folder for this evaluation
        eval_dir = out_root / f"{t['run_dir']}__eval"
        eval_dir.mkdir(parents=True, exist_ok=True)

        # Copy pred program to a clean pred_programs directory
        # The harness expects pred_program_path to contain pred_{gold_program_name}
        pred_prog_dir = eval_dir / "pred_programs"
        pred_prog_dir.mkdir(exist_ok=True)

        task = get_task(instance_id)
        target_name = "pred_" + task.gold_program_name
        import shutil

        shutil.copy2(pred_file, pred_prog_dir / target_name)

        run_id = f"r1_{arm}_s0_i{instance_id}"

        print(f"\n{'='*60}")
        print(f"Evaluating: instance={instance_id} arm={arm}")
        print(f"  program: {pred_file.name}  sha256={program_hash[:16]}...")
        print(f"  row_index: {row_map.get(instance_id)}")
        print(f"  run_id: {run_id}")
        print(f"{'='*60}")

        try:
            result = run_official_evaluation(
                task=task,
                pred_program_path=pred_prog_dir,
                benchmark_dir=DEFAULT_BENCHMARK_DIR,
                upstream_dir=DEFAULT_UPSTREAM_DIR,
                output_dir=eval_dir,
                run_id=run_id,
                parquet_path=DEFAULT_PARQUET,
                split=PINNED_SPLIT,
            )
        except EvaluatorUnavailable as e:
            print(f"BLOCKED: {e}")
            result_dict = {
                "task_id": task.task_key,
                "instance_id": instance_id,
                "arm": arm,
                "official_evaluation": False,
                "score": None,
                "error": str(e),
                "program_hash": program_hash,
                "source_run": t["run_dir"],
            }
            results.append(result_dict)
            continue

        result_dict = result.to_dict()
        result_dict["arm"] = arm
        result_dict["program_hash"] = program_hash
        result_dict["source_run"] = t["run_dir"]
        result_dict["score"] = (
            float(result.success_rate)
            if result.official_evaluation and result.success_rate is not None
            else None
        )
        results.append(result_dict)

        status = "OFFICIAL" if result.official_evaluation else "NOT_OFFICIAL"
        print(f"  → {status}: score={result_dict['score']} error={result.error}")

    # Write consolidated results
    summary = {
        "round": "001_r1",
        "mode": "retrospective_scoring_of_round_001_programs",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "n_evaluated": len(results),
        "n_official": sum(1 for r in results if r.get("official_evaluation")),
        "results": results,
    }
    out_path = out_root / "r1_evaluation_results.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nResults written to {out_path}")
    print(f"Official evaluations: {summary['n_official']} / {summary['n_evaluated']}")


if __name__ == "__main__":
    main()
