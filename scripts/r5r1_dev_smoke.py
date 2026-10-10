"""R5R1 DEV smoke: corrected engine with real actions."""
import sys
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.simulator.dgp.bio_expression import D1TaskConfig
from scitransfer.simulator.evaluator import score_submission
from scitransfer.simulator.engine import ExperimentEngine, Action

print("=== R5R1 DEV Smoke ===\n")

DEV_TASKS = [
    {"key": "dev_m1_a", "mechanism": "M1", "seed": 100},
    {"key": "dev_m1_b", "mechanism": "M1", "seed": 101},
    {"key": "dev_m2_a", "mechanism": "M2", "seed": 102},
    {"key": "dev_m2_b", "mechanism": "M2", "seed": 103},
]

def naive_policy(engine, step):
    """Naive: measure all, commit top genes."""
    if step == 0:
        return Action("MEASURE_QC", {"gene_subset": list(range(50))})
    elif step == 1:
        return Action("FIT_MODEL", {"genes": list(range(20))})
    else:
        # Commit top genes by p-value
        genes = []
        for g, v in engine._measured_genes.items():
            if "p_value" in v:
                genes.append((g, v["p_value"]))
        genes.sort(key=lambda x: x[1])
        top = [g for g, _ in genes[:10]] if genes else [0, 1, 2]
        return Action("COMMIT_HITS", {"gene_list": top})

def feedback_policy(engine, step):
    """Feedback-conditioned: allocate more reps if needed, then commit."""
    if step == 0:
        return Action("ALLOCATE_REPLICATE", {"n_reps": 3, "group": "control"})
    elif step == 1:
        return Action("ALLOCATE_REPLICATE", {"n_reps": 3, "group": "treatment"})
    elif step == 2:
        return Action("MEASURE_QC", {"gene_subset": list(range(30))})
    elif step == 3:
        return Action("FIT_MODEL", {"genes": list(range(15))})
    else:
        genes = []
        for g, v in engine._measured_genes.items():
            if "p_value" in v:
                genes.append((g, v["p_value"]))
        genes.sort(key=lambda x: x[1])
        top = [g for g, _ in genes[:8]] if genes else [0, 1]
        return Action("COMMIT_HITS", {"gene_list": top})

POLICIES = [("naive", naive_policy), ("feedback", feedback_policy)]
results = []

for task_cfg in DEV_TASKS:
    for policy_name, policy_fn in POLICIES:
        print(f"\n{task_cfg['key']}/{policy_name}:")
        
        config = D1TaskConfig(
            n_genes=100, n_samples=24, n_batches=2,
            mechanism=task_cfg["mechanism"],
            sigma_gamma=0.0 if task_cfg["mechanism"] == "M1" else 1.0,
        )
        
        engine = ExperimentEngine(task_cfg["seed"], task_cfg["key"], config)
        engine.reset()
        
        for step in range(10):
            action = policy_fn(engine, step)
            result = engine.step(action)
            if result.error:
                break
            if result.done:
                break
        
        if engine.submitted_genes:
            score = score_submission(
                engine.submitted_genes,
                engine._truth.true_non_null,
                engine.total_cost,
            )
            print(f"  FDP={score.fdp:.3f} Power={score.power:.3f} Cost={score.sample_cost} U={score.utility:.3f}")
            results.append({
                "task": task_cfg["key"], "mechanism": task_cfg["mechanism"],
                "policy": policy_name,
                "fdp": score.fdp, "power": score.power,
                "cost": score.sample_cost, "utility": score.utility,
            })
        else:
            print(f"  No submission")
            results.append({"task": task_cfg["key"], "policy": policy_name, "fdp": None})

# Summary
print(f"\n{'='*50}")
fdps = [r["fdp"] for r in results if r.get("fdp") is not None]
print(f"FDP range: {min(fdps):.3f} to {max(fdps):.3f}")
print(f"Non-trivial: {len(set(fdps)) > 1}")

Path("results/round_005_r1_dev.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"\nSaved to results/round_005_r1_dev.json")
