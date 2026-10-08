"""Run official evaluation for Task 85 (scoring logic unmodified)."""
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = REPO_ROOT / "benchmarks" / "ScienceAgentBench" / "benchmark"

# Load gold
gold_file = BENCHMARK / "eval_programs" / "gold_results" / "biopsykit_saliva_gold.json"
with open(gold_file) as f:
    gold = json.load(f)

# Load prediction
pred_file = REPO_ROOT / "pred_results" / "saliva_pred.json"
with open(pred_file) as f:
    pred = json.load(f)

print(f"Gold keys: {len(gold)}")
print(f"Pred keys: {len(pred)}")

# Official scoring logic (copied from biopsykit_saliva_eval.py - UNMODIFIED)
def eval():
    if set(gold.keys()) != set(pred.keys()):
        return 0, "N/A"
    
    for subject in gold.keys():
        gold_values = gold[subject]
        pred_values = pred[subject]
        for key in gold_values.keys():
            gold_value = gold_values[key]
            pred_value = pred_values[key]
            if isinstance(gold_value, float):
                try:
                    if not math.isclose(gold_value, pred_value, rel_tol=1e-9):
                        return 0, "N/A"
                except TypeError:
                    return 0, "N/A"
            elif isinstance(gold_value, str):
                if gold_value != pred_value:
                    return 0, "N/A"
    
    return 1, "N/A"

score, log_info = eval()
print(f"\nScore: {score}")
print(f"Log: {log_info}")

# Save result
result = {
    "task_id": "sab_verified_85",
    "instance_id": 85,
    "arm": "NO_STRATEGY",
    "official_evaluation": False,
    "modified_evaluator": True,
    "disclosure": "Direct execution of official scoring logic without Docker harness. The eval() function is UNMODIFIED from official biopsykit_saliva_eval.py.",
    "score": score,
    "success_rate": score,
    "log_info": log_info,
    "program_sha256_prefix": "58c7bc1f4ae66bfd",
    "source_run": "results/round_001_runs/sab_verified_85__NO_STRATEGY__seed0",
    "run_id": "r2_direct_85_nostrat_s0",
}

out_dir = REPO_ROOT / "results" / "round_001_r2_runs" / "sab_verified_85__NO_STRATEGY__seed0__eval"
out_dir.mkdir(parents=True, exist_ok=True)
result_file = out_dir / "eval_result.json"
result_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"\nResult saved to: {result_file}")
