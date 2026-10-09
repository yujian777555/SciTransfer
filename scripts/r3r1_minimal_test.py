"""R3R1: Minimal SciAgentGYM import and tool test."""
import sys
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src")

print("=== SciAgentGYM Minimal Test ===")

# Test 1: Import core modules
print("\n1. Importing core modules...")
try:
    from gym.env import MinimalSciEnv
    print("   gym.env.MinimalSciEnv: OK")
except Exception as e:
    print(f"   gym.env: FAIL - {e}")

try:
    from gym.tool import EnvironmentTool, ToolCall
    print("   gym.tool: OK")
except Exception as e:
    print(f"   gym.tool: FAIL - {e}")

try:
    from gym.toolbox import Toolbox
    print("   gym.toolbox: OK")
except Exception as e:
    print(f"   gym.toolbox: FAIL - {e}")

try:
    from gym.entities import Observation
    print("   gym.entities: OK")
except Exception as e:
    print(f"   gym.entities: FAIL - {e}")

# Test 2: Import evaluator
print("\n2. Importing evaluator...")
try:
    from gym.core.evaluator import extract_boxed_answer, calculate_answer_score
    print("   gym.core.evaluator: OK")
except Exception as e:
    print(f"   gym.core.evaluator: FAIL - {e}")

# Test 3: Check toolkits
print("\n3. Checking toolkits...")
import os
toolkits_dir = r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src\toolkits"
for d in os.listdir(toolkits_dir):
    dpath = os.path.join(toolkits_dir, d)
    if os.path.isdir(dpath):
        py_files = [f for f in os.listdir(dpath) if f.endswith('.py')]
        print(f"   {d}: {len(py_files)} .py files")

# Test 4: Try importing a simple physics tool
print("\n4. Testing tool import...")
try:
    sys.path.insert(0, toolkits_dir)
    # Try a simple physics tool
    from physics.optics.optics_tools_gym import *
    print("   physics.optics: OK")
except Exception as e:
    print(f"   physics.optics: FAIL - {e}")

print("\n=== Done ===")
