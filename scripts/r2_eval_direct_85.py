"""Run task 85 evaluation directly (MODIFIED EVALUATOR - disclosed).

This is a direct execution of the official evaluation script without Docker.
Labeled as MODIFIED EVALUATOR because it bypasses the official Docker harness.
The scoring logic (biopsykit_saliva_eval.py) is UNMODIFIED official code.
"""
import os
import sys
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = REPO_ROOT / "benchmarks" / "ScienceAgentBench" / "benchmark"
PRED_DIR = REPO_ROOT / "results" / "round_001_r2_runs" / "sab_verified_85__NO_STRATEGY__seed0__eval" / "pred_programs"

print("=== Task 85 NO_STRATEGY Evaluation (MODIFIED EVALUATOR) ===")
print("DISCLOSURE: Direct execution without Docker harness.")
print("Scoring logic is UNMODIFIED official biopsykit_saliva_eval.py")
print()

# 1. Run the predicted program
pred_file = PRED_DIR / "pred_saliva.py"
print(f"1. Running predicted program: {pred_file}")

# Create output directory
out_dir = REPO_ROOT / "results" / "round_001_r2_runs" / "sab_verified_85__NO_STRATEGY__seed0__eval"
pred_results = out_dir / "pred_results"
pred_results.mkdir(parents=True, exist_ok=True)

# Check if program expects a specific output path
prog_content = pred_file.read_text(encoding="utf-8")
print(f"   Program size: {len(prog_content)} bytes")

# Run the program
try:
    result = subprocess.run(
        [sys.executable, str(pred_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(out_dir),
    )
    print(f"   Exit code: {result.returncode}")
    if result.stdout:
        print(f"   stdout: {result.stdout[:200]}")
    if result.stderr:
        print(f"   stderr: {result.stderr[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")

# 2. Check output
output_file = pred_results / "saliva_pred.json"
if output_file.exists():
    print(f"\n2. Output file exists: {output_file}")
    pred_data = json.loads(output_file.read_text(encoding="utf-8"))
    print(f"   Keys: {list(pred_data.keys())[:5]}")
else:
    print(f"\n2. Output file NOT found: {output_file}")
    # Check what files were created
    print(f"   Files in {pred_results}: {list(pred_results.iterdir())}")
    sys.exit(1)

# 3. Run official evaluation
print(f"\n3. Running official evaluation script...")
gold_file = BENCHMARK / "eval_programs" / "gold_results" / "biopsykit_saliva_gold.json"

# Import and run the official eval
sys.path.insert(0, str(BENCHMARK / "eval_programs"))

# Change to the directory where eval expects files
os.chdir(str(REPO_ROOT))
# Create symlink/copy for eval to find files
import shutil
eval_pred_dir = REPO_ROOT / "pred_results"
eval_pred_dir.mkdir(exist_ok=True)
shutil.copy2(output_file, eval_pred_dir / "saliva_pred.json")

# Also make gold file accessible
gold_link = BENCHMARK / "eval_programs" / "gold_results" / "biopsykit_saliva_gold.json"

# Run eval
from biopsykit_saliva_eval import eval as official_eval
try:
    score, log_info = official_eval()
    print(f"   Score: {score}")
    print(f"   Log: {log_info}")
    
    # Save result
    result = {
        "task_id": "sab_verified_85",
        "instance_id": 85,
        "arm": "NO_STRATEGY",
        "official_evaluation": False,  # MODIFIED EVALUATOR
        "modified_evaluator": True,
        "disclosure": "Direct execution without Docker harness. Scoring logic is unmodified official code.",
        "score": score,
        "success_rate": score,
        "log_info": log_info,
        "program_sha256": "58c7bc1f4ae66bfd",
        "source_run": "results/round_001_runs/sab_verified_85__NO_STRATEGY__seed0",
        "run_id": "r2_direct_85_nostrat_s0",
    }
    
    result_file = out_dir / "eval_result.json"
    result_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\n   Result saved to: {result_file}")
    
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Done ===")
