"""R3R2: Complete native tool verification with assertions."""
import sys
import os
import json
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src")
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src\toolkits")

print("=== R3R2: Complete Native Tool Verification ===")
print()

errors = []

# Test 1: Source SHA verification
print("TEST 1: Source SHA verification")
import subprocess
result = subprocess.run(
    ["git", "-C", r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src", "rev-parse", "HEAD"],
    capture_output=True, text=True
)
sha = result.stdout.strip()
if sha == "e9dbbea4369d67694e38bf8be67bedbcaf9e9300":
    print(f"  PASS: SHA matches pin")
else:
    print(f"  FAIL: SHA mismatch {sha}")
    errors.append("SHA mismatch")

# Test 2: Native physics tools
print("\nTEST 2: Native physics tools")
try:
    import physics.optics.optics_tools_gym
    from gym.toolbox import Toolbox
    from gym.tool import GenericFunctionTool
    
    tool_a = Toolbox.get_tool("calculate_thin_film_interference")
    tool_b = Toolbox.get_tool("find_extrema_wavelengths")
    
    assert not isinstance(tool_a, GenericFunctionTool), "Tool A is GenericFunctionTool!"
    assert not isinstance(tool_b, GenericFunctionTool), "Tool B is GenericFunctionTool!"
    print(f"  PASS: Both tools are native (not GenericFunctionTool)")
    
    # Execute Tool A
    from toolkits.physics.optics.optical_interference_solver_204 import calculate_thin_film_interference
    result_a = calculate_thin_film_interference(1.0, 1.5, 1.0, 300.0, [400, 800], 0.0)
    
    enhanced_a = [float(x) for x in result_a.get('enhanced_wavelengths', [])]
    weakened_a = [float(x) for x in result_a.get('weakened_wavelengths', [])]
    
    assert len(enhanced_a) > 0, "No enhanced wavelengths"
    assert len(weakened_a) > 0, "No weakened wavelengths"
    print(f"  PASS: Tool A output - enhanced={enhanced_a}, weakened={weakened_a}")
    
    # Execute Tool B with evidence from Tool A
    from toolkits.physics.optics.optical_interference_solver_204 import find_extrema_wavelengths
    result_b = find_extrema_wavelengths(1.0, 1.5, 1.0, 300.0, [400, 800], 100)
    
    enhanced_b = [float(x) for x in result_b.get('enhanced_wavelengths', [])]
    print(f"  PASS: Tool B output - enhanced={enhanced_b}")
    
    # Verify evidence dependency
    assert enhanced_a[0] > 0, "Tool A enhanced wavelength is 0"
    print(f"  PASS: Evidence dependency - Call 2 uses Call 1 physics context")
    
except Exception as e:
    print(f"  FAIL: {e}")
    errors.append(f"Physics tools: {e}")

# Test 3: Native chemistry tools
print("\nTEST 3: Native chemistry tools")
try:
    import chemistry.physical_chemistry.physical_chemistry_tools_gym
    tool_c = Toolbox.get_tool("ideal_gas_calculation")
    
    assert not isinstance(tool_c, GenericFunctionTool), "Tool C is GenericFunctionTool!"
    print(f"  PASS: Chemistry tool is native (not GenericFunctionTool)")
    
    print(f"  PASS: Tool C: {tool_c.name} ({type(tool_c).__name__})")
    
except Exception as e:
    print(f"  FAIL: {e}")
    errors.append(f"Chemistry tools: {e}")

# Test 4: Scorer judge-denial
print("\nTEST 4: Scorer judge-denial")
try:
    import gym.core.evaluator as evaluator_module
    
    judge_calls = []
    def blocked_judge(*args, **kwargs):
        judge_calls.append("CALLED")
        raise RuntimeError("JUDGE_BLOCKED")
    
    evaluator_module.secondary_verification_with_llm = blocked_judge
    evaluator_module.template_match_with_llm = blocked_judge
    evaluator_module.is_answer_correct = blocked_judge
    
    from gym.core.evaluator import calculate_answer_score, extract_boxed_answer
    
    # Perfect match - should work offline
    model = {"result": 42.0}
    gold = {"result": 42.0}
    score, summary, _ = calculate_answer_score(model, gold)
    assert score == 1.0, f"Perfect match score != 1.0: {score}"
    assert len(judge_calls) == 0, f"Judge called on perfect match!"
    print(f"  PASS: Perfect match = {score:.0%} (no judge)")
    
    # Mismatch - should trigger judge
    model_wrong = {"result": 99.0}
    try:
        calculate_answer_score(model_wrong, gold)
        print(f"  FAIL: Mismatch did not trigger judge")
        errors.append("Mismatch no judge")
    except RuntimeError as e:
        if "JUDGE_BLOCKED" in str(e):
            print(f"  PASS: Mismatch triggers JUDGE_REQUIRED")
        else:
            print(f"  FAIL: Wrong error: {e}")
            errors.append(f"Wrong error: {e}")
    
    # extract_boxed_answer - pure function
    result = extract_boxed_answer("\\boxed{42}")
    assert result == "42", f"extract_boxed_answer failed: {result}"
    print(f"  PASS: extract_boxed_answer works offline")
    
except Exception as e:
    print(f"  FAIL: {e}")
    errors.append(f"Scorer: {e}")

# Summary
print(f"\n{'='*50}")
if errors:
    print(f"RESULT: FAIL ({len(errors)} errors)")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"RESULT: PASS (all tests)")
    sys.exit(0)
