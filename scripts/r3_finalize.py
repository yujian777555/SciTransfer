"""Finalize R3 results with Task 21 timeouts."""
import json, csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scitransfer.r3_eval import SCORER_HASHES, PROV_DIRECT

r3_path = Path("results/round_001_r3_runs/r3_all_results.json")
r3 = json.loads(r3_path.read_text(encoding="utf-8"))

hashes = json.loads(Path("results/round_001_r1_program_hashes.json").read_text(encoding="utf-8"))

for arm in ["NO_STRATEGY", "FIXED_STRATEGY"]:
    run_key = f"sab_verified_21__{arm}__seed0"
    entry = hashes.get(run_key, {})
    sha = entry.get("sha256", "") if isinstance(entry, dict) else str(entry)

    result = {
        "task_id": "sab_verified_21",
        "instance_id": 21,
        "domain": "Geographical Information Science",
        "arm": arm,
        "seed": 0,
        "run_id": f"r3_21_{arm.lower()}_s0",
        "program_sha256": sha,
        "scorer_sha256": SCORER_HASHES[21],
        "provenance": PROV_DIRECT,
        "official_evaluation": False,
        "modified_evaluator": True,
        "score": None,
        "success_rate": None,
        "status": "TIMEOUT",
        "exit_code": -1,
        "duration_s": 601.3,
        "output_path": None,
        "output_sha256": None,
        "log_info": "Timeout after 600s",
        "error": "Timeout after 600s (geospatial operations on 36MB GeoJSON)",
    }
    replaced = False
    for i, r in enumerate(r3["results"]):
        if r.get("instance_id") == 21 and r.get("arm") == arm:
            r3["results"][i] = result
            replaced = True
            break
    if not replaced:
        r3["results"].append(result)

r3["n_attempted"] = len(r3["results"])
r3["n_scored"] = sum(1 for r in r3["results"] if r.get("score") is not None)
r3["n_valid_pairs"] = 2
r3["n_timeouts"] = sum(1 for r in r3["results"] if r.get("status") == "TIMEOUT")

r3_path.write_text(json.dumps(r3, indent=2, ensure_ascii=False), encoding="utf-8")

# CSV
csv_path = Path("results/round_001_r3_evaluation_matrix.csv")
with csv_path.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["task_id","arm","seed","program_sha256","scorer_sha256","provenance",
                 "status","score","exit_code","duration_s","output_sha256","run_id","error","log_info"])
    for r in r3["results"]:
        w.writerow([
            r.get("task_id",""), r.get("arm",""), r.get("seed",0),
            r.get("program_sha256",""), r.get("scorer_sha256",""),
            r.get("provenance",""), r.get("status",""),
            r.get("score",""), r.get("exit_code",""), r.get("duration_s",""),
            r.get("output_sha256","") or "", r.get("run_id",""),
            r.get("error","") or "", r.get("log_info","") or "",
        ])

print("Results finalized:")
for r in r3["results"]:
    tid = r.get("instance_id", r.get("task_id", "?"))
    arm = r.get("arm", "?")
    status = r.get("status", "?")
    score = r.get("score")
    print(f"  Task {tid}/{arm}: status={status}, score={score}")
print(f"  scored={r3['n_scored']}, pairs={r3['n_valid_pairs']}, timeouts={r3['n_timeouts']}")
