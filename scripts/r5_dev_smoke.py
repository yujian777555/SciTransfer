"""G2: DEV task calibration smoke - 4 tasks x 2 policies."""
import sys
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.simulator.dgp.bio_expression import D1TaskConfig
from scitransfer.simulator.evaluator import score_submission, compute_utility
from scitransfer.simulator.engine import ExperimentEngine, Action

print("=== R5 G2: DEV Task Calibration Smoke ===\n")

# 4 DEV tasks spanning 2 mechanisms
DEV_TASKS = [
    {"key": "dev_m1_1", "mechanism": "M1", "seed": 100},
    {"key": "dev_m1_2", "mechanism": "M1", "seed": 101},
    {"key": "dev_m2_1", "mechanism": "M2", "seed": 102},
    {"key": "dev_m2_2", "mechanism": "M2", "seed": 103},
]

# 2 blinded reference policies
def naive_policy(obs, step, budget_left):
    """Naive fixed-allocation: commit top genes by fold change."""
    fc = obs.gene_means_treatment / (obs.gene_means_control + 1e-6)
    top_genes = np.argsort(fc)[-20:].tolist()
    return Action("COMMIT_HITS", {"gene_list": top_genes}, cost=0)

def feedback_policy(obs, step, budget_left):
    """Feedback-conditioned: allocate more reps if variance is high."""
    high_var = np.sum(obs.gene_vars_control > obs.gene_means_control * 1.5)
    
    if step < 3 and budget_left > 5:
        # Allocate more replicates
        return Action("ALLOCATE_REPLICATE", {"n_reps": 2, "group": "control"}, cost=2)
    elif step < 5 and budget_left > 3:
        # Measure QC
        return Action("MEASURE_QC", {"gene_subset": list(range(20))}, cost=1)
    else:
        # Commit
        fc = obs.gene_means_treatment / (obs.gene_means_control + 1e-6)
        top_genes = np.argsort(fc)[-15:].tolist()
        return Action("COMMIT_HITS", {"gene_list": top_genes}, cost=0)

POLICIES = [
    ("naive_fixed", naive_policy),
    ("feedback_conditioned", feedback_policy),
]

results = []

for task_cfg in DEV_TASKS:
    for policy_name, policy_fn in POLICIES:
        print(f"\nTask: {task_cfg['key']} / Policy: {policy_name}")
        
        config = D1TaskConfig(
            n_genes=200, n_samples=30, n_batches=2,
            mechanism=task_cfg["mechanism"],
            sigma_gamma=0.0 if task_cfg["mechanism"] == "M1" else 1.0,
        )
        
        engine = ExperimentEngine(
            master_seed=task_cfg["seed"],
            task_key=task_cfg["key"],
            config=config,
        )
        
        obs = engine.reset()
        submitted_genes = None
        
        for step in range(10):
            budget_left = engine.max_budget - engine.total_cost
            action = policy_fn(obs, step, budget_left)
            result = engine.step(action)
            
            if result.done and action.action_type == "COMMIT_HITS":
                submitted_genes = action.parameters["gene_list"]
                break
            
            if result.error:
                print(f"  Error at step {step}: {result.error}")
                break
            
            obs = result.observation
        
        # Score
        if submitted_genes is not None:
            score = score_submission(
                submitted_genes,
                engine.truth.true_non_null,
                engine.total_cost,
            )
            utility = compute_utility(score)
            
            print(f"  FDP: {score.fdp:.3f}, Power: {score.power:.3f}, Cost: {score.sample_cost}")
            print(f"  Utility: {utility:.3f}")
            
            results.append({
                "task": task_cfg["key"],
                "mechanism": task_cfg["mechanism"],
                "policy": policy_name,
                "fdp": score.fdp,
                "power": score.power,
                "cost": score.sample_cost,
                "utility": utility,
                "n_reported": score.n_reported,
                "n_true_positives": score.n_true_positives,
                "n_false_positives": score.n_false_positives,
            })
        else:
            print(f"  No submission (budget exhausted or error)")
            results.append({
                "task": task_cfg["key"],
                "mechanism": task_cfg["mechanism"],
                "policy": policy_name,
                "fdp": None, "power": None, "cost": engine.total_cost,
                "utility": None,
            })

# Summary
print(f"\n{'='*50}")
print(f"Summary:")
for r in results:
    print(f"  {r['task']}/{r['policy']}: FDP={r['fdp']}, Power={r['power']}, Cost={r['cost']}")

# Check score variation
fdps = [r['fdp'] for r in results if r['fdp'] is not None]
powers = [r['power'] for r in results if r['power'] is not None]
print(f"\nScore variation:")
print(f"  FDP range: {min(fdps):.3f} to {max(fdps):.3f}" if fdps else "  No FDP scores")
print(f"  Power range: {min(powers):.3f} to {max(powers):.3f}" if powers else "  No power scores")
print(f"  Non-trivial variation: {len(set(fdps)) > 1 or len(set(powers)) > 1}")

# Save results
out_dir = Path("results/round_005_d1_dev.json")
out_dir.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
print(f"\nResults saved to {out_dir}")
