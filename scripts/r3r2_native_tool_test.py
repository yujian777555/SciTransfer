"""R3R2: Verify native upstream tools (NOT GenericFunctionTool)."""
import sys
import os
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src")
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src\toolkits")

print("=== R3R2: Native Upstream Tool Verification ===")

# Verify source SHA
import subprocess
result = subprocess.run(
    ["git", "-C", r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src", "rev-parse", "HEAD"],
    capture_output=True, text=True
)
sha = result.stdout.strip()
print(f"1. Source SHA: {sha}")
assert sha == "e9dbbea4369d67694e38bf8be67bedbcaf9e9300", f"SHA mismatch: {sha}"
print(f"   SHA matches pin: OK")

# Import upstream toolbox
from gym.toolbox import Toolbox
from gym.env import MinimalSciEnv
from gym.tool import ToolCall

# List registered tools
print(f"\n2. Registered upstream tools:")
try:
    # Try to get a real upstream tool
    tool = Toolbox.get_tool("calculate_thin_film_interference")
    print(f"   Tool: {tool.name}")
    print(f"   Type: {type(tool).__name__}")
    print(f"   Module: {type(tool).__module__}")
    print(f"   Description: {tool.description[:80]}...")
    
    # Verify it's NOT a GenericFunctionTool
    from gym.tool import GenericFunctionTool
    is_generic = isinstance(tool, GenericFunctionTool)
    print(f"   Is GenericFunctionTool: {is_generic}")
    assert not is_generic, "Tool is GenericFunctionTool, not native!"
    
except Exception as e:
    print(f"   FAIL: {e}")

# Execute native tool through environment
print(f"\n3. Execute native tool through MinimalSciEnv:")
try:
    env = MinimalSciEnv()
    env.add_tool(tool)
    reset_result = env.reset()
    print(f"   Tools: {reset_result.get('available_tools', [])}")
    
    # Tool Call 1: Native upstream tool
    action1 = ToolCall(
        id="call-1",
        name="calculate_thin_film_interference",
        arguments={"n1": 1.0, "n2": 1.5, "d": 300.0, "wavelength_range": [400, 800], "incidence_angle": 0.0},
    )
    result1 = env.step(action1)
    obs1 = result1.observation
    print(f"   Observation type: {type(obs1).__name__}")
    
    # Parse output
    if hasattr(obs1, 'observation'):
        import json
        try:
            data = json.loads(obs1.observation) if isinstance(obs1.observation, str) else obs1.observation
            print(f"   Output: {json.dumps(data, indent=2)[:200]}")
        except:
            print(f"   Output (raw): {str(obs1.observation)[:200]}")
    
    print(f"   Native tool executed: OK")
    
except Exception as e:
    print(f"   FAIL: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== Done ===")
