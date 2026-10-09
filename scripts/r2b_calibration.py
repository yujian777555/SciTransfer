"""Run R2B calibration episodes in DiscoveryWorld.

Bounded: 6-10 episodes total across 2+ task families.
No API cost (rule-based agent for environment verification).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.discoveryworld_adapter import Arm, run_episode, EpisodeTrace

OUTPUT_DIR = Path("results/round_002_calibration")

# Calibration plan: 2 task families x 3 arms x 1 seed = 6 episodes
CALIBRATION_PLAN = [
    {"scenario": "Combinatorial Chemistry", "difficulty": "Easy", "seed": 42},
    {"scenario": "Combinatorial Chemistry", "difficulty": "Easy", "seed": 43},
    {"scenario": "Archaeology Dating", "difficulty": "Easy", "seed": 42},
    {"scenario": "Archaeology Dating", "difficulty": "Easy", "seed": 43},
    {"scenario": "Plant Nutrients", "difficulty": "Easy", "seed": 42},
    {"scenario": "Reactor Lab", "difficulty": "Easy", "seed": 42},
]

ARMS = [Arm.NO_STRATEGY, Arm.FIXED_CONDITIONAL_STRATEGY]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_traces = []

    total_start = time.time()

    for plan in CALIBRATION_PLAN:
        for arm in ARMS:
            print(f"\n{'='*50}")
            print(f"Episode: {plan['scenario']} / {plan['difficulty']} / seed={plan['seed']} / {arm.value}")

            try:
                trace = run_episode(
                    scenario=plan["scenario"],
                    difficulty=plan["difficulty"],
                    seed=plan["seed"],
                    arm=arm,
                    max_steps=15,
                    max_seconds=60.0,
                )
                all_traces.append(trace)

                d = trace.to_dict()
                print(f"  status={d['status']}, score={d['final_score']}/{d['max_score']}, steps={d['steps_taken']}, decisions={d['n_decision_points']}")

                # Save individual trace
                trace_file = OUTPUT_DIR / f"{trace.episode_id}.json"
                trace_file.write_text(json.dumps(d, indent=2, default=str), encoding="utf-8")

            except Exception as e:
                print(f"  ERROR: {type(e).__name__}: {e}")
                all_traces.append(EpisodeTrace(
                    episode_id=f"r2b_{plan['scenario'].replace(' ','_')}_{arm.value}_s{plan['seed']}",
                    scenario=plan["scenario"], difficulty=plan["difficulty"],
                    seed=plan["seed"], arm=arm.value, agent_id="SimplePolicyAgent",
                    model="rule-based-v1", status="ERROR",
                    steps_taken=0, final_score=0, max_score=0, score_normalized=0,
                    n_decision_points=0, elapsed_s=0,
                ))

    total_elapsed = time.time() - total_start

    # Summary
    summary = {
        "round": "002_calibration",
        "environment": "DiscoveryWorld",
        "agent_type": "rule-based (no API cost)",
        "n_episodes": len(all_traces),
        "total_elapsed_s": round(total_elapsed, 1),
        "episodes": [t.to_dict() for t in all_traces],
        "score_distribution": {
            "min": min(t.final_score for t in all_traces),
            "max": max(t.final_score for t in all_traces),
            "all_zero": all(t.final_score == 0 for t in all_traces),
            "all_max": all(t.final_score == t.max_score for t in all_traces),
            "has_variation": len(set(t.final_score for t in all_traces)) > 1,
        },
    }

    (OUTPUT_DIR / "calibration_summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )

    print(f"\n{'='*50}")
    print(f"Calibration complete: {len(all_traces)} episodes in {total_elapsed:.1f}s")
    print(f"Score distribution: {summary['score_distribution']}")
    print(f"Saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
