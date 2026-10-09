"""R3R1: SciAgentGYM tool execution test - 2 sequential scientific tool calls."""
import sys
import os
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src")
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src\toolkits")

print("=== SciAgentGYM Tool Execution Test ===")

# Import environment and tools
from gym.env import MinimalSciEnv
from gym.tool import ToolCall
from gym.toolbox import Toolbox

# Check what tools are registered
print("\n1. Checking registered tools...")
try:
    # Try importing physics tools
    import importlib
    import pkgutil
    
    toolkits_path = r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src\toolkits"
    physics_path = os.path.join(toolkits_path, "physics")
    
    # Find tool files
    for root, dirs, files in os.walk(physics_path):
        for f in files:
            if f.endswith('_tools_gym.py'):
                print(f"   Found: {os.path.relpath(os.path.join(root, f), toolkits_path)}")
    
    # Try importing a specific tool
    print("\n2. Importing physics mechanics tools...")
    from physics.mechanics.mechanics_tools_gym import *
    print("   mechanics tools: OK")
    
except Exception as e:
    print(f"   FAIL: {e}")

# Try creating environment and calling tools
print("\n3. Testing environment...")
try:
    env = MinimalSciEnv()
    print(f"   Environment created: {env}")
    reset_result = env.reset()
    print(f"   Reset result: {reset_result}")
except Exception as e:
    print(f"   FAIL: {e}")

# Test scorer
print("\n4. Testing scorer...")
try:
    from gym.core.evaluator import extract_boxed_answer, calculate_answer_score
    
    # Test extract_boxed_answer
    test_response = "The answer is \\boxed{42}"
    extracted = extract_boxed_answer(test_response)
    print(f"   extract_boxed_answer('{test_response}') = '{extracted}'")
    
    # Test calculate_answer_score (pure function)
    model_answer = {"result": 42.0}
    gold_answer = {"result": 42.0}
    score, summary, details = calculate_answer_score(model_answer, gold_answer)
    print(f"   calculate_answer_score(exact match) = {score:.2%}")
    
    model_answer2 = {"result": 41.9}
    score2, summary2, _ = calculate_answer_score(model_answer2, gold_answer)
    print(f"   calculate_answer_score(near match) = {score2:.2%}")
    
except Exception as e:
    print(f"   FAIL: {e}")

print("\n=== Done ===")
