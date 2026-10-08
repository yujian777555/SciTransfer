"""R2 smoke test preparation: verify hashes and prepare evaluation directory."""
import sys
import json
import hashlib
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.benchmarks.scienceagentbench import (
    get_task,
    get_row_index_map,
    load_verified_tasks,
)

# 1. Verify program hashes
hashes_path = Path("results/round_001_r1_program_hashes.json")
hashes = json.loads(hashes_path.read_text(encoding="utf-8"))

# 2. Verify dataset parity
tasks = load_verified_tasks()
row_map = get_row_index_map()
print(f"Verified split: {len(tasks)} tasks")
print(f"Row map: {len(row_map)} entries")
for iid in [85, 16, 21]:
    print(f"  Task {iid} row index: {row_map.get(iid)}")

# 3. Prepare pred_programs for Task 85 NO_STRATEGY (smoke test)
run_name = "sab_verified_85__NO_STRATEGY__seed0"
run_dir = Path("results/round_001_runs") / run_name
pred_files = list(run_dir.glob("pred_*.py"))
if not pred_files:
    print(f"ERROR: No pred_*.py in {run_dir}")
    sys.exit(1)

pred = pred_files[0]
h = hashlib.sha256(pred.read_bytes()).hexdigest()
hash_entry = hashes.get(run_name, {})
expected_sha = hash_entry.get("sha256", "") if isinstance(hash_entry, dict) else str(hash_entry)
print(f"Program: {pred.name}, SHA256: {h[:16]}...")
print(f"Expected: {expected_sha[:16]}, Match: {h == expected_sha}")

if h != expected_sha:
    print("ERROR: Program hash mismatch!")
    sys.exit(1)

# 4. Prepare eval directory
eval_dir = Path("results/round_001_r2_runs") / (run_name + "__eval")
pred_dir = eval_dir / "pred_programs"
pred_dir.mkdir(parents=True, exist_ok=True)

task = get_task(85)
target_name = "pred_" + task.gold_program_name
shutil.copy2(pred, pred_dir / target_name)
print(f"Copied to: {pred_dir / target_name}")

# 5. Verify benchmark structure
bench = Path("benchmarks/ScienceAgentBench/benchmark")
for item in ["eval_programs", "gold_programs", "datasets"]:
    p = bench / item
    if p.exists():
        count = len(list(p.iterdir()))
        print(f"{item}: OK ({count} items)")
    else:
        print(f"{item}: MISSING")

print("\nSmoke test preparation complete.")
print(f"Ready to evaluate Task 85 NO_STRATEGY from: {pred_dir}")
