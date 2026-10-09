"""R3R1: Scorer integrity test with judge-denial firewall."""
import sys
import os
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src")

print("=== R3R1: Scorer Integrity Test ===")
print("Firewall: LLM judge calls will be BLOCKED\n")

# Monkeypatch to block any LLM judge calls
import gym.core.evaluator as evaluator_module

original_is_answer_correct = evaluator_module.is_answer_correct
original_secondary = evaluator_module.secondary_verification_with_llm
original_template = evaluator_module.template_match_with_llm

judge_calls = []

def blocked_is_answer_correct(*args, **kwargs):
    judge_calls.append("is_answer_correct")
    raise RuntimeError("JUDGE_BLOCKED: LLM judge call attempted but blocked by firewall")

def blocked_secondary(*args, **kwargs):
    judge_calls.append("secondary_verification_with_llm")
    raise RuntimeError("JUDGE_BLOCKED: LLM secondary verification attempted but blocked")

def blocked_template(*args, **kwargs):
    judge_calls.append("template_match_with_llm")
    raise RuntimeError("JUDGE_BLOCKED: LLM template match attempted but blocked")

evaluator_module.is_answer_correct = blocked_is_answer_correct
evaluator_module.secondary_verification_with_llm = blocked_secondary
evaluator_module.template_match_with_llm = blocked_template

# Test calculate_answer_score (pure function, no LLM)
from gym.core.evaluator import calculate_answer_score, extract_boxed_answer

print("1. Perfect match test:")
model = {"result": 42.0, "label": "test"}
gold = {"result": 42.0, "label": "test"}
score, summary, details = calculate_answer_score(model, gold)
print(f"   Score: {score:.2%}")
print(f"   Summary: {summary}")
print(f"   Judge calls so far: {len(judge_calls)}")

print("\n2. Wrong answer test:")
model_wrong = {"result": 99.0, "label": "test"}
score2, summary2, _ = calculate_answer_score(model_wrong, gold)
print(f"   Score: {score2:.2%}")
print(f"   Summary: {summary2}")
print(f"   Judge calls: {len(judge_calls)}")

print("\n3. Missing field test:")
model_missing = {"result": 42.0}
score3, summary3, _ = calculate_answer_score(model_missing, gold)
print(f"   Score: {score3:.2%}")
print(f"   Summary: {summary3}")
print(f"   Judge calls: {len(judge_calls)}")

print("\n4. Near-correct (within tolerance) test:")
model_near = {"result": 42.01, "label": "test"}  # 0.02% off
score4, summary4, _ = calculate_answer_score(model_near, gold)
print(f"   Score: {score4:.2%}")
print(f"   Summary: {summary4}")
print(f"   Judge calls: {len(judge_calls)}")

print("\n5. extract_boxed_answer test:")
test_cases = [
    ("The answer is \\boxed{42}", "42"),
    ("\\boxed{3.14}", "3.14"),
    ("No boxed answer", None),
    ("\\boxed{result}", "result"),
]
for text, expected in test_cases:
    result = extract_boxed_answer(text)
    status = "PASS" if result == expected else "FAIL"
    print(f"   {status}: extract_boxed_answer('{text[:30]}...') = '{result}'")

print(f"\n6. Firewall summary:")
print(f"   Total judge calls attempted: {len(judge_calls)}")
print(f"   Judge calls: {judge_calls}")
print(f"   calculate_answer_score works offline: {'YES' if len(judge_calls) == 0 else 'NO - judge was called'}")

print("\n=== Done ===")
