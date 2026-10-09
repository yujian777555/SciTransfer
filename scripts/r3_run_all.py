"""Run R3 evaluation for all 6 programs. Direct original scorer, isolated workspaces."""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.r3_eval import (
    PROV_DIRECT,
    EvalResult,
    evaluate_one,
    load_frozen_hashes,
    sha256_file,
    SCORER_HASHES,
)

TASKS = [85, 16, 21]
ARMS = ["NO_STRATEGY", "FIXED_STRATEGY"]

def main():
    results = []
    for task_id in TASKS:
        for arm in ARMS:
            print(f"\n{'='*60}")
            print(f"R3: Task {task_id} / {arm}")
            result = evaluate_one(task_id, arm, seed=0)
            results.append(result)
            d = result.to_dict()
            print(f"  status={d['status']}, score={d['score']}, duration={d['duration_s']}s")
            if d.get("error"):
                print(f"  error: {d['error'][:100]}")

    # Summary
    n_success = sum(1 for r in results if r.status == "SUCCESS")
    n_timeout = sum(1 for r in results if r.status == "TIMEOUT")
    n_failed = sum(1 for r in results if r.status == "EXECUTION_FAILED")
    n_hash = sum(1 for r in results if r.status == "HASH_MISMATCH")
    n_scored = sum(1 for r in results if r.score is not None)

    # Valid pairs (both arms scored)
    pairs = {}
    for r in results:
        key = r.task_id
        if key not in pairs:
            pairs[key] = {}
        pairs[key][r.arm] = r.score
    valid_pairs = sum(
        1 for t, arms in pairs.items()
        if arms.get("NO_STRATEGY") is not None and arms.get("FIXED_STRATEGY") is not None
    )

    summary = {
        "round": "001_r3",
        "provenance": PROV_DIRECT,
        "scorer_hashes": SCORER_HASHES,
        "n_attempted": len(results),
        "n_executed": n_success + n_failed,
        "n_scored_direct_original": n_scored,
        "n_scored_official_docker": 0,
        "n_valid_pairs": valid_pairs,
        "n_timeouts": n_timeout,
        "n_hash_mismatches": n_hash,
        "n_execution_failed": n_failed,
        "results": [r.to_dict() for r in results],
    }

    # Save JSON
    out_json = Path("results/round_001_r3_runs/r3_all_results.json")
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    # Save CSV matrix
    out_csv = Path("results/round_001_r3_evaluation_matrix.csv")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "task_id", "arm", "seed", "program_sha256", "scorer_sha256",
            "provenance", "status", "score", "exit_code", "duration_s",
            "output_sha256", "run_id", "error", "log_info",
        ])
        for r in results:
            d = r.to_dict()
            writer.writerow([
                d["task_id"], d["arm"], d["seed"],
                d["program_sha256"], d["scorer_sha256"],
                d["provenance"], d["status"], d["score"],
                d["exit_code"], d["duration_s"],
                d["output_sha256"] or "", d["run_id"],
                d["error"] or "", d["log_info"] or "",
            ])

    print(f"\n{'='*60}")
    print(f"R3 Summary:")
    print(f"  attempted={summary['n_attempted']}, executed={summary['n_executed']}")
    print(f"  scored={n_scored}, timeouts={n_timeout}, failed={n_failed}, hash_mismatch={n_hash}")
    print(f"  valid_pairs={valid_pairs}")
    print(f"  results: {out_json}")
    print(f"  matrix:  {out_csv}")


if __name__ == "__main__":
    main()
