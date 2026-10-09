"""G3: LLM micro-pilot with identical agent across arms.

Uses DeepSeek API. At most 4 scored episodes, $1 budget cap.
Strategy is the ONLY difference between arms.
"""
import warnings
warnings.filterwarnings("ignore")

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
from scitransfer.secure_input import build_model_input, get_safe_task_description

# DeepSeek API
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-v4-pro"

# Budget tracking
TOTAL_COST_USD = 0.0
MAX_COST_USD = 1.0
MAX_EPISODES = 4
MAX_STEPS = 15
MAX_TOKENS = 2048

STRATEGY_TEXT = (
    "Before writing the full solution, first write a minimal baseline that only loads "
    "the data and saves a trivial but correctly formatted output at the required path. "
    "Then iterate: add one analysis step at a time and re-run to verify each step produces "
    "a valid intermediate result before adding the next."
)


def call_llm(messages: list[dict]) -> tuple[str, int, int]:
    """Call DeepSeek API. Returns (response_text, tokens_in, tokens_out)."""
    global TOTAL_COST_USD

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "temperature": 0.0,
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.load(r)
        text = resp["choices"][0]["message"]["content"] or ""
        usage = resp.get("usage", {})
        tokens_in = usage.get("prompt_tokens", 0)
        tokens_out = usage.get("completion_tokens", 0)
        # Cost estimate (deepseek-v4-pro pricing)
        cost = (tokens_in * 0.5 + tokens_out * 1.5) / 1e6
        TOTAL_COST_USD += cost
        return text, tokens_in, tokens_out
    except Exception as e:
        return f"ERROR: {e}", 0, 0


def extract_action(text: str) -> dict:
    """Extract action JSON from LLM response."""
    import re
    # Look for JSON object with "action" key
    match = re.search(r'\{[^}]*"action"[^}]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"action": "MOVE_DIRECTION", "arg1": "east"}


def run_llm_episode(scenario: str, difficulty: str, seed: int, arm: str) -> dict:
    """Run one episode with LLM agent."""
    global TOTAL_COST_USD

    print(f"\n{'='*50}")
    print(f"Episode: {scenario} / seed={seed} / {arm}")

    api = DiscoveryWorldAPI()
    api.loadScenario(scenario, difficulty, seed, 1)

    # Initial score (trusted)
    scorecard = api.getTaskScorecard()
    initial_score = scorecard[0].get("score", 0) if scorecard else 0
    max_score = scorecard[0].get("maxScore", 0) if scorecard else 0
    task_desc = get_safe_task_description(scorecard[0]) if scorecard else ""

    print(f"  Initial: {initial_score}/{max_score}")

    # Build system prompt (IDENTICAL for both arms except strategy)
    system_prompt = (
        "You are a scientific research agent in a virtual lab. "
        "Your task is to complete the scientific objective by taking actions in the environment.\n\n"
        f"Task: {task_desc}\n\n"
        "Available actions (JSON format):\n"
        '- {"action": "MOVE_DIRECTION", "arg1": "north"|"east"|"south"|"west"}\n'
        '- {"action": "PICKUP", "arg1": <object_uuid>}\n'
        '- {"action": "USE", "arg1": <tool_uuid>, "arg2": <target_uuid>}\n'
        '- {"action": "DROP", "arg1": <object_uuid>}\n'
        '- {"action": "OPEN", "arg1": <object_uuid>}\n'
        '- {"action": "ACTIVATE", "arg1": <object_uuid>}\n\n'
        "Respond with ONLY a JSON action object. Choose actions that make scientific progress toward the task goal."
    )

    if arm == "FIXED_CONDITIONAL_STRATEGY":
        system_prompt += f"\n\nStrategy: {STRATEGY_TEXT}"

    messages = [{"role": "system", "content": system_prompt}]

    actions_taken = []
    n_valid = 0
    n_invalid = 0

    for step in range(MAX_STEPS):
        if TOTAL_COST_USD > MAX_COST_USD:
            print(f"  BUDGET EXCEEDED at step {step}")
            break

        # Get observation
        obs = api.getAgentObservation(0)
        ui = obs.get("ui", {})
        accessible = ui.get("accessibleEnvironmentObjects", [])
        inventory = ui.get("inventoryObjects", [])

        # Build model input (whitelist)
        safe_obs = {
            "accessible_objects": [{"uuid": o.get("uuid"), "name": o.get("name")} for o in accessible if isinstance(o, dict)],
            "inventory": [{"uuid": o.get("uuid"), "name": o.get("name")} for o in inventory if isinstance(o, dict)],
            "agent_location": str(ui.get("agentLocation", "")),
            "last_action_message": str(ui.get("lastActionMessage", "")),
        }

        user_msg = f"Step {step}. Observation: {json.dumps(safe_obs)}. What action should you take?"
        messages.append({"role": "user", "content": user_msg})

        # Call LLM
        response_text, t_in, t_out = call_llm(messages)
        messages.append({"role": "assistant", "content": response_text})

        # Extract action
        action_json = extract_action(response_text)
        actions_taken.append({"step": step, "action": action_json, "response_preview": response_text[:100]})

        # Execute action
        result = api.performAgentAction(0, action_json)
        success = result.get("success", False)
        errors = result.get("errors", [])

        if success:
            n_valid += 1
        else:
            n_invalid += 1

        # Record feedback
        feedback = f"Action {action_json} -> success={success}, errors={errors[:1]}"
        messages.append({"role": "user", "content": feedback})

        api.tick()

    # Final score
    scorecard2 = api.getTaskScorecard()
    final_score = scorecard2[0].get("score", 0) if scorecard2 else 0

    print(f"  Final: {final_score}/{max_score}, delta={final_score - initial_score}")
    print(f"  Valid actions: {n_valid}, Invalid: {n_invalid}")
    print(f"  Cost so far: ${TOTAL_COST_USD:.4f}")

    return {
        "scenario": scenario,
        "seed": seed,
        "arm": arm,
        "initial_score": initial_score,
        "final_score": final_score,
        "score_delta": final_score - initial_score,
        "max_score": max_score,
        "n_valid_actions": n_valid,
        "n_invalid_actions": n_invalid,
        "n_steps": len(actions_taken),
        "actions": actions_taken,
    }


def main():
    if not API_KEY:
        print("BLOCKED: DEEPSEEK_API_KEY not set")
        return

    print("=== R2 LLM Micro-Pilot ===")
    print(f"Model: {MODEL}, Budget: ${MAX_COST_USD}, Max episodes: {MAX_EPISODES}")
    print(f"Pre-registration: experiments/round_002_r2_preregistration.json")

    # 2 scenarios x 2 arms = 4 episodes
    plan = [
        ("Combinatorial Chemistry", "Easy", 200),
        ("Archaeology Dating", "Easy", 200),
    ]

    results = []
    for scenario, difficulty, seed in plan:
        for arm in ["NO_STRATEGY", "FIXED_CONDITIONAL_STRATEGY"]:
            if len(results) >= MAX_EPISODES:
                break
            if TOTAL_COST_USD > MAX_COST_USD:
                print(f"BUDGET EXCEEDED: ${TOTAL_COST_USD:.4f}")
                break

            result = run_llm_episode(scenario, difficulty, seed, arm)
            results.append(result)

    # Summary
    print(f"\n{'='*50}")
    print(f"Total cost: ${TOTAL_COST_USD:.4f}")
    print(f"Episodes: {len(results)}")
    for r in results:
        print(f"  {r['scenario']}/{r['arm']}: delta={r['score_delta']}, valid={r['n_valid_actions']}")

    # Save results
    output_dir = Path("results/round_002_r2_pilot")
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "model": MODEL,
        "total_cost_usd": round(TOTAL_COST_USD, 6),
        "n_episodes": len(results),
        "episodes": results,
    }
    (output_dir / "r2_llm_pilot_results.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )
    print(f"\nResults saved to {output_dir}/r2_llm_pilot_results.json")


if __name__ == "__main__":
    main()
