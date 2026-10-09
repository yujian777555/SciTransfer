"""R3: Score already-run programs with official scorer. Can also run individual tasks."""
import json
import os
import sys
import time
import subprocess
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.r3_eval import (
    PROV_DIRECT, SCORER_HASHES,
    load_frozen_hashes, load_official_scorer,
    sha256_file, verify_program_hash, find_output, score_with_original,
    prepare_isolated_workdir, run_program_isolated,
    R3_RUNS, REPO_ROOT,
)

TASKS = [85, 16, 21]
ARMS = ["NO_STRATEGY", "FIXED_STRATEGY"]


def score_existing(task_id, arm, seed=0):
    """Score a program that already has output in its isolated workdir."""
    run_id = f"r3_{task_id}_{arm.lower()}_s{seed}"
    workdir = R3_RUNS / run_id

    if not workdir.exists():
        return {"error": f"Workdir not found: {workdir}", "status": "ERROR"}

    # Verify hash
    hashes = load_frozen_hashes()
    run_key = f"sab_verified_{task_id}__{arm}__seed{seed}"
    expected_sha = hashes.get(run_key, "")

    source_dir = REPO_ROOT / "results" / "round_001_runs" / run_key
    pred_files = list(source_dir.glob("pred_*.py"))
    if not pred_files:
        return {"error": f"Program not found", "status": "ERROR"}

    actual_sha = sha256_file(pred_files[0])
    if actual_sha != expected_sha:
        return {"error": f"SHA mismatch", "status": "HASH_MISMATCH",
                "program_sha256": actual_sha}

    # Check for output
    output_path = find_output(workdir, task_id)
    if output_path is None:
        return {"error": "No output", "status": "NO_OUTPUT",
                "program_sha256": actual_sha}

    output_sha = sha256_file(output_path)

    # Score with official scorer
    try:
        score, log_info = score_with_original(task_id, workdir)
        return {
            "task_id": f"sab_verified_{task_id}",
            "instance_id": task_id,
            "arm": arm,
            "seed": seed,
            "run_id": run_id,
            "program_sha256": actual_sha,
            "scorer_sha256": SCORER_HASHES[task_id],
            "provenance": PROV_DIRECT,
            "official_evaluation": False,
            "modified_evaluator": True,
            "score": score,
            "success_rate": score,
            "status": "SUCCESS" if score is not None else "ERROR",
            "output_path": str(output_path),
            "output_sha256": output_sha,
            "log_info": log_info,
            "error": None,
        }
    except Exception as e:
        # Official harness catches scorer exceptions and returns 0
        return {
            "task_id": f"sab_verified_{task_id}",
            "instance_id": task_id,
            "arm": arm,
            "seed": seed,
            "run_id": run_id,
            "program_sha256": actual_sha,
            "scorer_sha256": SCORER_HASHES[task_id],
            "provenance": PROV_DIRECT,
            "official_evaluation": False,
            "modified_evaluator": True,
            "score": 0,
            "success_rate": 0,
            "status": "SUCCESS",
            "output_path": str(output_path),
            "output_sha256": output_sha,
            "log_info": f"EXCEPTION: {e}",
            "error": f"Scorer exception (official harness returns 0): {e}",
        }


def main():
    results = []
    for task_id in TASKS:
        for arm in ARMS:
            print(f"Scoring Task {task_id}/{arm}...", end=" ")
            r = score_existing(task_id, arm)
            results.append(r)
            print(f"status={r.get('status')}, score={r.get('score')}")

    n_scored = sum(1 for r in results if r.get("score") is not None)
    pairs = {}
    for r in results:
        tid = r.get("instance_id")
        if tid not in pairs:
            pairs[tid] = {}
        pairs[tid][r.get("arm")] = r.get("score")
    valid_pairs = sum(
        1 for t, a in pairs.items()
        if a.get("NO_STRATEGY") is not None and a.get("FIXED_STRATEGY") is not None
    )

    summary = {
        "round": "001_r3",
        "provenance": PROV_DIRECT,
        "n_attempted": len(results),
        "n_scored": n_scored,
        "n_valid_pairs": valid_pairs,
        "results": results,
    }

    out = Path("results/round_001_r3_runs/r3_all_results.json")
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{n_scored}/6 scored, {valid_pairs} valid pairs")
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()
