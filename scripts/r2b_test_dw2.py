"""Check DiscoveryWorld API signatures."""
import warnings
warnings.filterwarnings("ignore")
from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

import inspect

api = DiscoveryWorldAPI()

# Check loadScenario signature
print("loadScenario signature:", inspect.signature(api.loadScenario))
print("loadScenario docstring:", api.loadScenario.__doc__)

# Check performAgentAction signature
print("\nperformAgentAction signature:", inspect.signature(api.performAgentAction))
print("performAgentAction docstring:", api.performAgentAction.__doc__)

# Check getAgentObservation
print("\ngetAgentObservation signature:", inspect.signature(api.getAgentObservation))

# Check getTaskScorecard
print("\ngetTaskScorecard signature:", inspect.signature(api.getTaskScorecard))

# Try loading with correct args
print("\nLoading 'Plant Nutrients' with difficulty Easy...")
api.loadScenario("Plant Nutrients", "Easy", "1", 42)
print("Loaded OK")

scorecard = api.getTaskScorecard()
print(f"Scorecard: {scorecard}")

obs = api.getAgentObservation()
print(f"Observation type: {type(obs)}")
if isinstance(obs, str):
    print(f"Observation (first 500 chars): {obs[:500]}")
elif isinstance(obs, dict):
    for k, v in list(obs.items())[:5]:
        val_str = str(v)[:200]
        print(f"  {k}: {val_str}")

actions = api.listKnownActions()
print(f"\nAvailable actions ({len(actions)}):")
for a in actions[:15]:
    print(f"  {a}")
