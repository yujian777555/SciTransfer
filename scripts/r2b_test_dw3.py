"""Test DiscoveryWorld with different scenarios."""
import warnings
warnings.filterwarnings("ignore")
from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

api = DiscoveryWorldAPI()

# Try multiple scenarios
test_scenarios = [
    ("Combinatorial Chemistry", "Easy", "1", 42),
    ("Archaeology Dating", "Easy", "1", 42),
    ("Reactor Lab", "Easy", "1", 42),
    ("Space Sick", "Easy", "1", 42),
    ("Proteomics", "Easy", "1", 42),
]

for name, diff, var, seed in test_scenarios:
    try:
        api.loadScenario(name, diff, seed, 1)
        scorecard = api.getTaskScorecard()
        steps = api.getStepCounter()
        complete = api.areTasksComplete()
        actions = api.listKnownActions()
        obs = api.getAgentObservation(0)

        print(f"\n=== {name} ({diff}) ===")
        print(f"  Loaded OK, steps={steps}, complete={complete}")
        print(f"  Scorecard: {scorecard}")
        print(f"  Actions: {len(actions)}")
        if isinstance(obs, str):
            print(f"  Obs: {obs[:150]}...")
        elif isinstance(obs, dict):
            print(f"  Obs keys: {list(obs.keys())[:5]}")
        break  # Just test first working one
    except Exception as e:
        print(f"\n=== {name} FAILED: {type(e).__name__}: {str(e)[:80]} ===")
        continue
