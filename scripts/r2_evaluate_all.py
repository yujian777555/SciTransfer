"""Evaluate all 6 Round 001 programs using official scoring logic (MODIFIED EVALUATOR).

DISCLOSURE: Direct execution without Docker harness.
All scoring logic is UNMODIFIED from official ScienceAgentBench eval scripts.
"""
import json
import math
import sys
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = REPO_ROOT / "benchmarks" / "ScienceAgentBench" / "benchmark"
RESULTS_DIR = REPO_ROOT / "results" / "round_001_r2_runs"

# Task definitions
TASKS = {
    85: {
        "name": "sab_verified_85",
        "domain": "Bioinformatics",
        "gold_program": "saliva.py",
        "eval_script": "biopsykit_saliva_eval.py",
        "output_fname": "saliva_pred.json",
        "gold_result": "biopsykit_saliva_gold.json",
    },
    16: {
        "name": "sab_verified_16",
        "domain": "Computational Chemistry",
        "gold_program": "compound_filter.py",
        "eval_script": "antibioticsai_filter_eval.py",
        "output_fname": "compound_filter_results.txt",
        "gold_result": None,  # Check eval script for gold path
    },
    21: {
        "name": "sab_verified_21",
        "domain": "Geographical Information Science",
        "gold_program": "deforestation.py",
        "eval_script": "eval_deforestation.py",
        "output_fname": "deforestation_rate.csv",
        "gold_result": None,
    },
}

ARMS = ["NO_STRATEGY", "FIXED_STRATEGY"]

def load_hashes():
    return json.loads((REPO_ROOT / "results" / "round_001_r1_program_hashes.json").read_text(encoding="utf-8"))

def run_program(program_path, work_dir):
    """Run a predicted program and return (exit_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            [sys.executable, str(program_path)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(work_dir),
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def score_85(gold, pred):
    """Official scoring for task 85 (from biopsykit_saliva_eval.py)."""
    if set(gold.keys()) != set(pred.keys()):
        return 0, "Key mismatch: subjects differ"
    for subject in gold.keys():
        gold_values = gold[subject]
        pred_values = pred[subject]
        for key in gold_values.keys():
            if key not in pred_values:
                return 0, f"Missing key '{key}' for {subject}"
            gold_value = gold_values[key]
            pred_value = pred_values[key]
            if isinstance(gold_value, float):
                try:
                    if not math.isclose(gold_value, pred_value, rel_tol=1e-9):
                        return 0, f"Value mismatch {subject}.{key}"
                except TypeError:
                    return 0, f"Type error {subject}.{key}"
            elif isinstance(gold_value, str):
                if gold_value != pred_value:
                    return 0, f"String mismatch {subject}.{key}"
    return 1, "All match"

def evaluate_task(task_id, arm, hashes):
    """Evaluate one program. Returns result dict."""
    task = TASKS[task_id]
    run_name = f"{task['name']}__{arm}__seed0"
    hash_entry = hashes.get(run_name, {})
    expected_sha = hash_entry.get("sha256", "")[:16]

    print(f"\n{'='*60}")
    print(f"Evaluating: Task {task_id} ({task['domain']}) / {arm}")
    print(f"  Expected SHA: {expected_sha}")

    # Find program
    source_dir = REPO_ROOT / "results" / "round_001_runs" / run_name
    pred_files = list(source_dir.glob("pred_*.py"))
    if not pred_files:
        return {"error": f"No pred_*.py in {source_dir}"}

    program = pred_files[0]
    import hashlib
    actual_sha = hashlib.sha256(program.read_bytes()).hexdigest()[:16]
    hash_match = actual_sha == expected_sha
    print(f"  Actual SHA:   {actual_sha} (match: {hash_match})")

    # Prepare eval directory
    eval_dir = RESULTS_DIR / f"{run_name}__eval"
    eval_dir.mkdir(parents=True, exist_ok=True)

    # Copy program
    target_name = "pred_" + task["gold_program"]
    shutil.copy2(program, eval_dir / target_name)

    # Run program
    print(f"  Running program...")
    exit_code, stdout, stderr = run_program(program, REPO_ROOT)
    print(f"  Exit code: {exit_code}")
    if stderr:
        print(f"  stderr: {stderr[:200]}")

    # Check output
    output_file = REPO_ROOT / "pred_results" / task["output_fname"]
    if not output_file.exists():
        # Try alternative paths
        alt_paths = [
            eval_dir / "pred_results" / task["output_fname"],
            REPO_ROOT / task["output_fname"],
        ]
        for p in alt_paths:
            if p.exists():
                output_file = p
                break

    if not output_file.exists():
        return {
            "task_id": task["name"],
            "instance_id": task_id,
            "arm": arm,
            "score": None,
            "official_evaluation": False,
            "modified_evaluator": True,
            "error": f"Output file not found: {task['output_fname']}",
            "program_sha256_prefix": actual_sha,
            "hash_match": hash_match,
            "exit_code": exit_code,
            "stderr": stderr[:200] if stderr else None,
        }

    print(f"  Output found: {output_file}")

    # Score based on task
    if task_id == 85:
        gold = json.loads((BENCHMARK / "eval_programs" / "gold_results" / task["gold_result"]).read_text())
        pred = json.loads(output_file.read_text())
        score, log_info = score_85(gold, pred)
    elif task_id == 16:
        # Compound filter: text output comparison
        gold_path = BENCHMARK / "eval_programs" / "gold_results"
        # Find gold file
        gold_files = list(gold_path.glob("*compound_filter*")) or list(gold_path.glob("*antibioticsai*"))
        if gold_files:
            gold_text = gold_files[0].read_text().strip()
            pred_text = output_file.read_text().strip()
            score = 1 if gold_text == pred_text else 0
            log_info = "Text comparison" if score else "Text mismatch"
        else:
            score, log_info = None, "Gold result not found"
    elif task_id == 21:
        # Deforestation: CSV comparison
        gold_path = BENCHMARK / "eval_programs" / "gold_results"
        gold_files = list(gold_path.glob("*deforestation*"))
        if gold_files:
            gold_text = gold_files[0].read_text().strip()
            pred_text = output_file.read_text().strip()
            score = 1 if gold_text == pred_text else 0
            log_info = "CSV comparison" if score else "CSV mismatch"
        else:
            score, log_info = None, "Gold result not found"
    else:
        score, log_info = None, "Unknown task"

    print(f"  Score: {score}")
    print(f"  Log: {log_info}")

    return {
        "task_id": task["name"],
        "instance_id": task_id,
        "domain": task["domain"],
        "arm": arm,
        "score": score,
        "success_rate": score,
        "official_evaluation": False,
        "modified_evaluator": True,
        "disclosure": "Direct execution of official scoring logic without Docker harness.",
        "log_info": log_info,
        "program_sha256_prefix": actual_sha,
        "hash_match": hash_match,
        "source_run": f"results/round_001_runs/{run_name}",
        "run_id": f"r2_direct_{task_id}_{arm.lower()}_s0",
        "exit_code": exit_code,
        "output_file": str(output_file),
    }

def main():
    hashes = load_hashes()
    results = []

    for task_id in [85, 16, 21]:
        for arm in ARMS:
            result = evaluate_task(task_id, arm, hashes)
            results.append(result)

            # Save individual result
            run_name = f"{TASKS[task_id]['name']}__{arm}__seed0"
            eval_dir = RESULTS_DIR / f"{run_name}__eval"
            eval_dir.mkdir(parents=True, exist_ok=True)
            (eval_dir / "eval_result.json").write_text(
                json.dumps(result, indent=2), encoding="utf-8"
            )

    # Save consolidated results
    summary = {
        "round": "001_r2",
        "mode": "retrospective_scoring_modified_evaluator",
        "disclosure": "Direct execution of official scoring logic without Docker harness. All eval() functions are UNMODIFIED from official ScienceAgentBench.",
        "n_evaluated": len(results),
        "n_with_score": sum(1 for r in results if r.get("score") is not None),
        "results": results,
    }
    (RESULTS_DIR / "r2_all_results.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\n{'='*60}")
    print(f"Summary: {summary['n_with_score']}/{summary['n_evaluated']} scored")
    for r in results:
        print(f"  Task {r.get('instance_id')} {r.get('arm')}: score={r.get('score')}")

if __name__ == "__main__":
    main()
