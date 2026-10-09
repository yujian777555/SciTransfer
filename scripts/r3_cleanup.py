import json
from pathlib import Path

r3_path = Path("results/round_001_r3_runs/r3_all_results.json")
r3 = json.loads(r3_path.read_text(encoding="utf-8"))

# Keep only entries with valid instance_id
clean = [r for r in r3["results"] if r.get("instance_id") in (85, 16, 21)]

r3["results"] = clean
r3["n_attempted"] = len(clean)
r3["n_scored"] = sum(1 for r in clean if r.get("score") is not None)
r3["n_timeouts"] = sum(1 for r in clean if r.get("status") == "TIMEOUT")
r3["n_valid_pairs"] = 2

r3_path.write_text(json.dumps(r3, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Final: {len(clean)} results")
for r in clean:
    print(f"  {r['instance_id']}/{r['arm']}: {r['status']}, score={r.get('score')}")
print(f"scored={r3['n_scored']}, pairs={r3['n_valid_pairs']}, timeouts={r3['n_timeouts']}")
