"""Discover official DiscoveryWorld action schema."""
import warnings
warnings.filterwarnings("ignore")

from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

api = DiscoveryWorldAPI()

# Get known actions
actions = api.listKnownActions()
print("=== listKnownActions() ===")
for a in actions:
    print(f"  {a}")

# Get action descriptions
print("\n=== additionalActionDescriptionString() ===")
desc = api.additionalActionDescriptionString()
print(desc)

# Load a scenario and inspect action format
print("\n=== Loading Combinatorial Chemistry ===")
api.loadScenario("Combinatorial Chemistry", "Easy", 42, 1)

# Get observation structure
obs = api.getAgentObservation(0)
print(f"\nObservation type: {type(obs)}")
if isinstance(obs, dict):
    print(f"Observation keys: {list(obs.keys())}")
    # Check for UI structure (where object UUIDs would be)
    ui = obs.get("ui", {})
    if isinstance(ui, dict):
        print(f"UI keys: {list(ui.keys())}")

# Try a valid action and check response format
print("\n=== Testing valid action ===")
result = api.performAgentAction(0, {"action": "MOVE_DIRECTION", "arg1": "EAST"})
print(f"Result type: {type(result)}")
print(f"Result: {result}")

# Test invalid action
print("\n=== Testing invalid action ===")
result2 = api.performAgentAction(0, {"action": "moveAgentForward"})
print(f"Result: {result2}")

# Get scorecard structure (for trusted evaluator only)
scorecard = api.getTaskScorecard()
if scorecard and len(scorecard) > 0:
    sc = scorecard[0]
    print(f"\n=== Scorecard keys ===")
    print(list(sc.keys()))
    print(f"\nSub-task keys: {list(sc.get('scoreCard', [{}])[0].keys()) if sc.get('scoreCard') else 'none'}")
