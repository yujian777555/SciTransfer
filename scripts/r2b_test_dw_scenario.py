"""Test DiscoveryWorld scenario creation and multi-step interaction."""
import warnings
warnings.filterwarnings("ignore")

from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

# Create API
api = DiscoveryWorldAPI()
print("API created")

# Get valid scenarios
scenarios = api.getValidScenarios()
print(f"Valid scenarios: {scenarios}")

# Load plant_growing scenario
print("\nLoading plant_growing (seed=42)...")
api.loadScenario("plant_growing", seed=42)
print("Scenario loaded")

# Get task scorecard
scorecard = api.getTaskScorecard()
print(f"Scorecard: {scorecard}")

# Get step counter
steps = api.getStepCounter()
print(f"Steps: {steps}")

# List known actions
actions = api.listKnownActions()
print(f"\nKnown actions ({len(actions)}):")
for a in actions[:10]:
    print(f"  {a}")

# Get agent observation
obs = api.getAgentObservation()
print(f"\nObservation type: {type(obs)}")
if isinstance(obs, dict):
    print(f"Observation keys: {list(obs.keys())}")
    for k, v in list(obs.items())[:5]:
        if isinstance(v, str) and len(v) > 100:
            print(f"  {k}: {v[:100]}...")
        else:
            print(f"  {k}: {v}")
elif isinstance(obs, str):
    print(f"Observation: {obs[:300]}")

# Try tick
print("\nTicking...")
api.tick()
steps2 = api.getStepCounter()
print(f"Steps after tick: {steps2}")

# Check if tasks complete
complete = api.areTasksComplete()
print(f"Tasks complete: {complete}")
