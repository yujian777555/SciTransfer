import warnings
warnings.filterwarnings("ignore")
from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

api = DiscoveryWorldAPI()
api.loadScenario("Combinatorial Chemistry", "Easy", 42, 1)

for direction in ["north", "east", "south", "west"]:
    result = api.performAgentAction(0, {"action": "MOVE_DIRECTION", "arg1": direction})
    success = result.get("success")
    errors = result.get("errors")
    print(f"{direction}: success={success}, errors={errors}")
    api.tick()
