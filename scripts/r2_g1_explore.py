"""G1: Explore then find real scientific actions."""
import warnings
warnings.filterwarnings("ignore")
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
from scitransfer.secure_input import get_safe_task_description


def explore_and_act():
    api = DiscoveryWorldAPI()
    SEED = 200
    api.loadScenario("Combinatorial Chemistry", "Easy", SEED, 1)

    scorecard = api.getTaskScorecard()
    initial_score = scorecard[0].get("score", 0) if scorecard else 0
    max_score = scorecard[0].get("maxScore", 0) if scorecard else 0
    print(f"Initial: {initial_score}/{max_score}")

    scientific_actions = []
    steps = []

    # Phase 1: Explore to find objects
    print("\n=== Phase 1: Exploration ===")
    for i in range(8):
        obs = api.getAgentObservation(0)
        ui = obs.get("ui", {})
        accessible = ui.get("accessibleEnvironmentObjects", [])
        names = [o.get("name", "") for o in accessible if isinstance(o, dict)]
        print(f"  step {i}: accessible={names}")

        # Find pickable objects (not wall/floor)
        pickable = [o for o in accessible if isinstance(o, dict) and o.get("name", "").lower() not in ("wall", "floor", "ceiling")]

        if pickable:
            print(f"  FOUND pickable: {[o.get('name') for o in pickable]}")
            break

        # Try to move
        direction = ["east", "north", "west", "south"][i % 4]
        result = api.performAgentAction(0, {"action": "MOVE_DIRECTION", "arg1": direction})
        success = result.get("success", False)
        print(f"  MOVE {direction}: success={success}")
        api.tick()

    # Phase 2: Try scientific actions on found objects
    print("\n=== Phase 2: Scientific Actions ===")
    for i in range(8):
        obs = api.getAgentObservation(0)
        ui = obs.get("ui", {})
        accessible = ui.get("accessibleEnvironmentObjects", [])
        inventory = ui.get("inventoryObjects", [])

        pickable = [o for o in accessible if isinstance(o, dict) and o.get("name", "").lower() not in ("wall", "floor", "ceiling")]

        if pickable:
            obj = pickable[0]
            uid = int(obj["uuid"])
            print(f"  PICKUP {obj['name']} (uuid={uid})")
            result = api.performAgentAction(0, {"action": "PICKUP", "arg1": uid})
            success = result.get("success", False)
            errors = result.get("errors", [])
            print(f"    success={success}, errors={errors[:1]}")
            if success:
                scientific_actions.append({"action": "PICKUP", "target": obj["name"], "step": i})
            api.tick()

            # Check state change
            obs2 = api.getAgentObservation(0)
            inv2 = obs2.get("ui", {}).get("inventoryObjects", [])
            inv_names = [o.get("name") for o in inv2 if isinstance(o, dict)]
            print(f"    inventory: {inv_names}")
        else:
            # Try USE on inventory items
            inv = ui.get("inventoryObjects", [])
            if len(inv) >= 2:
                uid1 = int(inv[0]["uuid"])
                uid2 = int(inv[1]["uuid"])
                print(f"  USE {inv[0].get('name')} on {inv[1].get('name')}")
                result = api.performAgentAction(0, {"action": "USE", "arg1": uid1, "arg2": uid2})
                success = result.get("success", False)
                print(f"    success={success}")
                if success:
                    scientific_actions.append({"action": "USE", "tool": inv[0].get("name"), "target": inv[1].get("name"), "step": i})
                api.tick()
            else:
                # Move to find more
                direction = ["east", "north", "west", "south"][i % 4]
                result = api.performAgentAction(0, {"action": "MOVE_DIRECTION", "arg1": direction})
                print(f"  MOVE {direction}: success={result.get('success', False)}")
                api.tick()

    # Final score
    scorecard2 = api.getTaskScorecard()
    final_score = scorecard2[0].get("score", 0) if scorecard2 else 0
    print(f"\nFinal: {final_score}/{max_score}")
    print(f"Delta: {final_score - initial_score}")
    print(f"\nScientific actions: {len(scientific_actions)}")
    for a in scientific_actions:
        print(f"  {a}")

    return {
        "seed": SEED,
        "initial_score": initial_score,
        "final_score": final_score,
        "score_delta": final_score - initial_score,
        "n_scientific_actions": len(scientific_actions),
        "scientific_actions": scientific_actions,
    }


if __name__ == "__main__":
    result = explore_and_act()
    print(f"\n{json.dumps(result, indent=2)}")
