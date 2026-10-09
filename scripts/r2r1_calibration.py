"""R2-R1 calibration: 2 scenarios x 2 arms x 1 seed = 4 episodes + 2 controls."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.discoveryworld_r2r1 import Arm, run_episode_r2r1

OUTPUT_DIR = Path("results/round_002_r1_calibration")

# Plan: 2 scenario families x 2 arms x 1 seed = 4 episodes
CALIBRATION_PLAN = [
    {"scenario": "Combinatorial Chemistry", "difficulty": "Easy", "seed": 100},
    {"scenario": "Archaeology Dating", "difficulty": "Easy", "seed": 100},
]

ARMS = [Arm.NO_STRATEGY, Arm.FIXED_CONDITIONAL_STRATEGY]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_results = []
    total_start = time.time()

    for plan in CALIBRATION_PLAN:
        for arm in ARMS:
            print(f"\n{'='*50}")
            print(f"Episode: {plan['scenario']} / seed={plan['seed']} / {arm.value}")

            try:
                result = run_episode_r2r1(
                    scenario=plan["scenario"],
                    difficulty=plan["difficulty"],
                    seed=plan["seed"],
                    arm=arm,
                    max_steps=15,
                    max_seconds=60.0,
                )
                all_results.append(result)

                # Save candidate-safe trace
                trace_file = OUTPUT_DIR / f"{result.episode_id}_trace.json"
                trace_file.write_text(
                    json.dumps(result.to_candidate_dict(), indent=2, default=str),
                    encoding="utf-8"
                )

                # Save trusted scorecard separately (restricted)
                trusted_file = OUTPUT_DIR / f"{result.episode_id}_trusted.json"
                trusted_file.write_text(
                    json.dumps(result.to_trusted_dict(), indent=2, default=str),
                    encoding="utf-8"
                )

                print(f"  status={result.status}")
                print(f"  initial={result.initial_score}, final={result.final_score}, delta={result.score_delta}")
                print(f"  valid={result.n_valid_actions}, invalid={result.n_invalid_actions}")
                print(f"  decision_points={result.n_decision_points}")
                print(f"  events={len(result.events)}")

            except Exception as e:
                print(f"  ERROR: {type(e).__name__}: {e}")

    total_elapsed = time.time() - total_start

    # Summary
    summary = {
        "round": "002_r1_calibration",
        "environment": "DiscoveryWorld",
        "agent_type": "rule-based EvidencePolicyAgent (no API cost)",
        "n_episodes": len(all_results),
        "total_elapsed_s": round(total_elapsed, 1),
        "episodes": [
            {
                "episode_id": r.episode_id,
                "scenario": r.scenario,
                "arm": r.arm,
                "status": r.status,
                "initial_score": r.initial_score,
                "final_score": r.final_score,
                "score_delta": r.score_delta,
                "n_valid_actions": r.n_valid_actions,
                "n_invalid_actions": r.n_invalid_actions,
                "n_decision_points": r.n_decision_points,
                "n_events": len(r.events),
            }
            for r in all_results
        ],
        "score_variation": {
            "min_delta": min(r.score_delta for r in all_results) if all_results else 0,
            "max_delta": max(r.score_delta for r in all_results) if all_results else 0,
            "has_variation": len(set(r.score_delta for r in all_results)) > 1 if all_results else False,
        },
    }

    (OUTPUT_DIR / "r1_calibration_summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )

    print(f"\n{'='*50}")
    print(f"Calibration complete: {len(all_results)} episodes in {total_elapsed:.1f}s")
    print(f"Score variation: {summary['score_variation']}")


if __name__ == "__main__":
    main()
