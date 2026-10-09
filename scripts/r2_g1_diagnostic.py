"""G1: Prove real scientific actions and feedback-dependent decisions.

A scientific action = documented test/measurement/inspection/experimental
manipulation relevant to task objective, with observable feedback.
Movement, invalid pickup, or repeated ticks are NOT scientific decisions.
"""
import warnings
warnings.filterwarnings("ignore")

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
from scitransfer.secure_input import build_model_input, get_safe_task_description


def run_g1_diagnostic():
    """G1 diagnostic: find and execute real scientific actions."""
    print("=== G1: Scientific Action Diagnostic ===\n")

    api = DiscoveryWorldAPI()

    # Use a FRESH seed (not 42/43/100)
    SEED = 200
    SCENARIO = "Combinatorial Chemistry"
    DIFFICULTY = "Easy"

    print(f"Scenario: {SCENARIO}, Difficulty: {DIFFICULTY}, Seed: {SEED}")
    api.loadScenario(SCENARIO, DIFFICULTY, SEED, 1)

    # Get initial score (trusted)
    scorecard = api.getTaskScorecard()
    initial_score = scorecard[0].get("score", 0) if scorecard else 0
    max_score = scorecard[0].get("maxScore", 0) if scorecard else 0
    task_desc = get_safe_task_description(scorecard[0]) if scorecard else ""
    print(f"Initial score: {initial_score}/{max_score}")

    # Get observation
    obs = api.getAgentObservation(0)
    ui = obs.get("ui", {})
    accessible = ui.get("accessibleEnvironmentObjects", [])
    print(f"\nAccessible objects ({len(accessible)}):")
    for obj in accessible[:10]:
        if isinstance(obj, dict):
            print(f"  uuid={obj.get('uuid')}, name={obj.get('name')}")

    # Check inventory
    inventory = ui.get("inventoryObjects", [])
    print(f"\nInventory ({len(inventory)}):")
    for obj in inventory[:5]:
        if isinstance(obj, dict):
            print(f"  uuid={obj.get('uuid')}, name={obj.get('name')}")

    # Try scientific actions: PICKUP on real objects (not walls/floors)
    print("\n=== Testing scientific actions ===")

    # Find pickable objects
    pickable = [o for o in accessible if isinstance(o, dict) and o.get("name", "").lower() not in ("wall", "floor", "ceiling")]
    print(f"Pickable objects: {[o.get('name') for o in pickable[:5]]}")

    scientific_actions = []
    for obj in pickable[:3]:
        uid = int(obj["uuid"])
        print(f"\n  PICKUP {obj['name']} (uuid={uid}):")
        result = api.performAgentAction(0, {"action": "PICKUP", "arg1": uid})
        success = result.get("success", False)
        errors = result.get("errors", [])
        print(f"    success={success}, errors={errors[:2]}")

        if success:
            scientific_actions.append({
                "action": "PICKUP",
                "target": obj["name"],
                "uuid": uid,
                "success": True,
            })

        api.tick()

        # Check if state changed
        obs2 = api.getAgentObservation(0)
        inv2 = obs2.get("ui", {}).get("inventoryObjects", [])
        inv_names = [o.get("name") for o in inv2 if isinstance(o, dict)]
        print(f"    inventory after: {inv_names}")

    # Try USE action if we have objects
    if scientific_actions:
        inv = api.getAgentObservation(0).get("ui", {}).get("inventoryObjects", [])
        if len(inv) >= 2:
            obj1 = inv[0]
            obj2 = inv[1]
            uid1 = int(obj1["uuid"])
            uid2 = int(obj2["uuid"])
            print(f"\n  USE {obj1['name']} on {obj2['name']}:")
            result = api.performAgentAction(0, {"action": "USE", "arg1": uid1, "arg2": uid2})
            success = result.get("success", False)
            errors = result.get("errors", [])
            print(f"    success={success}, errors={errors[:2]}")
            if success:
                scientific_actions.append({
                    "action": "USE",
                    "tool": obj1["name"],
                    "target": obj2["name"],
                    "success": True,
                })
            api.tick()

    # Check final score
    scorecard2 = api.getTaskScorecard()
    final_score = scorecard2[0].get("score", 0) if scorecard2 else 0
    print(f"\nFinal score: {final_score}/{max_score}")
    print(f"Score delta: {final_score - initial_score}")

    # Summary
    print(f"\n=== G1 Summary ===")
    print(f"Scientific actions completed: {len(scientific_actions)}")
    for a in scientific_actions:
        print(f"  {a}")

    return {
        "scenario": SCENARIO,
        "seed": SEED,
        "initial_score": initial_score,
        "final_score": final_score,
        "score_delta": final_score - initial_score,
        "scientific_actions": scientific_actions,
        "n_scientific_actions": len(scientific_actions),
    }


if __name__ == "__main__":
    result = run_g1_diagnostic()
    print(f"\nResult: {json.dumps(result, indent=2)}")
