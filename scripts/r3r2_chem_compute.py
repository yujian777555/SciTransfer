import sys
sys.path.insert(0, r'C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src')
sys.path.insert(0, r'C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src\toolkits')

import chemistry.physical_chemistry.physical_chemistry_tools_gym
from gym.toolbox import Toolbox
from gym.env import MinimalSciEnv
from gym.tool import ToolCall
import json

tool = Toolbox.get_tool('ideal_gas_calculation')
print(f'Tool: {tool.name} ({type(tool).__name__})')

env = MinimalSciEnv()
env.add_tool(tool)
env.reset()

# Provide P, V, T, gas_constant -> compute n
action = ToolCall(
    id='chem-1',
    name='ideal_gas_calculation',
    arguments={
        'pressure': 101325,
        'volume': 0.0224,
        'temperature': 273.15,
        'gas_constant': 8.314,
        'units': {'P': 'Pa', 'V': 'm³', 'T': 'K', 'R': 'J/(mol·K)'}
    }
)
result = env.step(action)
obs = result.observation
print(f'Result type: {type(obs).__name__}')
if hasattr(obs, 'observation'):
    raw = obs.observation
    print(f'Output: {raw[:500]}')
    try:
        data = json.loads(raw)
        print(f'Parsed: {json.dumps(data, indent=2)[:500]}')
    except:
        print(f'Raw output (not JSON)')
