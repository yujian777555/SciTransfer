"""R3R1: Scorer integrity - document judge dependency."""
import sys
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src")

print("=== R3R1: Scorer Integrity Analysis ===")

# Block all LLM judge calls
import gym.core.evaluator as evaluator_module

judge_calls = []

def blocked_judge(*args, **kwargs):
    judge_calls.append("LLM_JUDGE_CALLED")
    raise RuntimeError("JUDGE_BLOCKED")

evaluator_module.secondary_verification_with_llm = blocked_judge
evaluator_module.template_match_with_llm = blocked_judge
evaluator_module.is_answer_correct = blocked_judge

from gym.core.evaluator import calculate_answer_score, extract_boxed_answer

print("\n1. Perfect match (no judge needed):")
model = {"result": 42.0}
gold = {"result": 42.0}
try:
    score, summary, _ = calculate_answer_score(model, gold)
    print(f"   Score: {score:.2%} - {summary}")
    print(f"   Judge calls: {len(judge_calls)}")
except Exception as e:
    print(f"   Exception: {e}")

print("\n2. Wrong answer (judge attempted):")
model_wrong = {"result": 99.0}
try:
    score, summary, _ = calculate_answer_score(model_wrong, gold)
    print(f"   Score: {score:.2%} - {summary}")
except RuntimeError as e:
    print(f"   JUDGE_REQUIRED: {e}")
    print(f"   This confirms calculate_answer_score is NOT pure offline")

print(f"\n3. Finding:")
print(f"   - Perfect match: works offline (no judge)")
print(f"   - Mismatch: requires LLM judge (secondary_verification_with_llm)")
print(f"   - Label: JUDGE_REQUIRED / OFFLINE_SCORER_NOT_EQUIVALENT")
print(f"   - This is NOT an authentic original official offline score for mismatch paths")

print("\n4. extract_boxed_answer (pure function):")
tests = [
    ("\\boxed{42}", "42"),
    ("answer: \\boxed{3.14}", "3.14"),
    ("no box", None),
]
for text, expected in tests:
    result = extract_boxed_answer(text)
    status = "PASS" if result == expected else "FAIL"
    print(f"   {status}: '{text}' -> '{result}'")

print("\n=== Conclusion ===")
print("SciAgentGYM scorer has TWO modes:")
print("  1. calculate_answer_score: pure for exact match, LLM judge for mismatches")
print("  2. is_answer_correct: always uses LLM judge")
print("For offline $0 evaluation: only exact-match path is judge-free.")
print("Mismatch paths trigger JUDGE_REQUIRED.")
