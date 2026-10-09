"""Explore DiscoveryWorld observation UI structure for object UUIDs."""
import warnings
warnings.filterwarnings("ignore")
import json

from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

api = DiscoveryWorldAPI()
api.loadScenario("Combinatorial Chemistry", "Easy", 42, 1)

obs = api.getAgentObservation(0)
ui = obs.get("ui", {})

# Explore accessible objects
print("=== accessibleEnvironmentObjects ===")
objs = ui.get("accessibleEnvironmentObjects", [])
print(f"Count: {len(objs)}")
for o in objs[:5]:
    if isinstance(o, dict):
        print(f"  keys: {list(o.keys())}")
        print(f"  sample: {json.dumps({k: str(v)[:50] for k, v in o.items()}, indent=2)}")

# Explore inventory
print("\n=== inventoryObjects ===")
inv = ui.get("inventoryObjects", [])
print(f"Count: {len(inv)}")

# Explore nearby objects
print("\n=== nearbyObjects ===")
nearby = ui.get("nearbyObjects", [])
print(f"Count: {len(nearby)}")

# Try MOVE_DIRECTION with correct format
print("\n=== Testing MOVE_DIRECTION ===")
# Check what directions are valid
for direction in ["north", "NORTH", "up", "forward", "1", "0"]:
    result = api.performAgentAction(0, {"action": "MOVE_DIRECTION", "arg1": direction})
    print(f"  direction={direction!r}: {result}")
    api.tick()  # Reset for next attempt

# Get initial scorecard (for trusted evaluator)
print("\n=== Initial Scorecard (TRUSTED EVALUATOR ONLY) ===")
scorecard = api.getTaskScorecard()
if scorecard:
    sc = scorecard[0]
    print(f"score={sc.get('score')}/{sc.get('maxScore')}, completed={sc.get('completed')}, completedSuccessfully={sc.get('completedSuccessfully')}")
    for sub in sc.get("scoreCard", []):
        print(f"  {sub.get('name')}: {sub.get('score')}/{sub.get('maxScore')} ({sub.get('completed')})")
