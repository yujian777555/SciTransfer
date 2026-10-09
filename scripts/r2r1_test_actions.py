"""Test correct DiscoveryWorld action format."""
import warnings
warnings.filterwarnings("ignore")
from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

api = DiscoveryWorldAPI()
api.loadScenario("Combinatorial Chemistry", "Easy", 42, 1)

# Test MOVE_DIRECTION with lowercase
print("=== MOVE_DIRECTION arg1=north ===")
result = api.performAgentAction(0, {"action": "MOVE_DIRECTION", "arg1": "north"})
print(f"Result: {result}")

api.tick()

# Test MOVE_DIRECTION arg1=east
print("\n=== MOVE_DIRECTION arg1=east ===")
result = api.performAgentAction(0, {"action": "MOVE_DIRECTION", "arg1": "east"})
print(f"Result: {result}")

api.tick()

# Test PICKUP with UUID from observation
obs = api.getAgentObservation(0)
ui = obs.get("ui", {})
accessible = ui.get("accessibleEnvironmentObjects", [])
print(f"\n=== Accessible objects ===")
for o in accessible[:5]:
    print(f"  uuid={o['uuid']}, name={o['name']}")

if accessible:
    uid = int(accessible[0]["uuid"])
    print(f"\n=== PICKUP arg1={uid} ===")
    result = api.performAgentAction(0, {"action": "PICKUP", "arg1": uid})
    print(f"Result: {result}")

api.tick()

# Check scorecard
scorecard = api.getTaskScorecard()
if scorecard:
    sc = scorecard[0]
    print(f"\n=== Score after actions ===")
    print(f"score={sc.get('score')}/{sc.get('maxScore')}")
    for sub in sc.get("scoreCard", []):
        print(f"  {sub.get('name')}: {sub.get('score')}/{sub.get('maxScore')}")
