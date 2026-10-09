"""G3: Run individual LLM episodes with incremental saving."""
import warnings
warnings.filterwarnings("ignore")
import json, os, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
from scitransfer.secure_input import get_safe_task_description

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-v4-pro"
STRATEGY_TEXT = "Before writing the full solution, first write a minimal baseline that only loads the data and saves a trivial but correctly formatted output at the required path. Then iterate: add one analysis step at a time."

OUTPUT_DIR = Path("results/round_002_r2_pilot")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load existing results
results_file = OUTPUT_DIR / "r2_llm_pilot_results.json"
if results_file.exists():
    existing = json.loads(results_file.read_text())
else:
    existing = {"model": MODEL, "total_cost_usd": 0, "episodes": []}

def call_llm(messages):
    global existing
    payload = {"model": MODEL, "messages": messages, "max_tokens": 1024, "temperature": 0.0}
    req = urllib.request.Request(f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.load(r)
        text = resp["choices"][0]["message"]["content"] or ""
        usage = resp.get("usage", {})
        cost = (usage.get("prompt_tokens",0)*0.5 + usage.get("completion_tokens",0)*1.5)/1e6
        existing["total_cost_usd"] = round(existing.get("total_cost_usd",0) + cost, 6)
        return text
    except Exception as e:
        return f"ERROR: {e}"

def extract_action(text):
    import re
    m = re.search(r'\{[^}]*"action"[^}]*\}', text)
    if m:
        try: return json.loads(m.group())
        except: pass
    return {"action": "MOVE_DIRECTION", "arg1": "east"}

def run_episode(scenario, difficulty, seed, arm):
    print(f"\n=== {scenario} / seed={seed} / {arm} ===")
    api = DiscoveryWorldAPI()
    api.loadScenario(scenario, difficulty, seed, 1)
    sc = api.getTaskScorecard()
    initial = sc[0].get("score", 0) if sc else 0
    max_s = sc[0].get("maxScore", 0) if sc else 0
    task_desc = get_safe_task_description(sc[0]) if sc else ""
    print(f"  Initial: {initial}/{max_s}")

    sys_prompt = (f"You are a scientific research agent. Task: {task_desc}\n"
        'Respond with ONLY a JSON action: {"action": "MOVE_DIRECTION", "arg1": "north"|"east"|"south"|"west"} or '
        '{"action": "PICKUP", "arg1": <uuid>} or {"action": "USE", "arg1": <uuid>, "arg2": <uuid>}')
    if arm == "FIXED_CONDITIONAL_STRATEGY":
        sys_prompt += f"\nStrategy: {STRATEGY_TEXT}"

    messages = [{"role": "system", "content": sys_prompt}]
    n_valid = n_invalid = 0

    for step in range(10):
        obs = api.getAgentObservation(0)
        ui = obs.get("ui", {})
        acc = [{"uuid": o.get("uuid"), "name": o.get("name")} for o in ui.get("accessibleEnvironmentObjects", []) if isinstance(o, dict)]
        inv = [{"uuid": o.get("uuid"), "name": o.get("name")} for o in ui.get("inventoryObjects", []) if isinstance(o, dict)]
        messages.append({"role": "user", "content": f"Step {step}. Objects: {json.dumps(acc)}. Inventory: {json.dumps(inv)}. What action?"})

        resp = call_llm(messages)
        messages.append({"role": "assistant", "content": resp})
        action = extract_action(resp)
        result = api.performAgentAction(0, action)
        success = result.get("success", False)
        if success: n_valid += 1
        else: n_invalid += 1
        messages.append({"role": "user", "content": f"Result: success={success}, errors={result.get('errors',[])[:1]}"})
        api.tick()

    sc2 = api.getTaskScorecard()
    final = sc2[0].get("score", 0) if sc2 else 0
    print(f"  Final: {final}/{max_s}, delta={final-initial}, valid={n_valid}, invalid={n_invalid}")
    print(f"  Cost: ${existing['total_cost_usd']:.4f}")

    return {"scenario": scenario, "seed": seed, "arm": arm,
            "initial_score": initial, "final_score": final, "score_delta": final-initial,
            "max_score": max_s, "n_valid_actions": n_valid, "n_invalid_actions": n_invalid}

# Check which episodes are done
done = {(e["scenario"], e["seed"], e["arm"]) for e in existing["episodes"]}
plan = [
    ("Combinatorial Chemistry", "Easy", 200, "NO_STRATEGY"),
    ("Combinatorial Chemistry", "Easy", 200, "FIXED_CONDITIONAL_STRATEGY"),
    ("Archaeology Dating", "Easy", 200, "NO_STRATEGY"),
    ("Archaeology Dating", "Easy", 200, "FIXED_CONDITIONAL_STRATEGY"),
]

for scenario, diff, seed, arm in plan:
    if (scenario, seed, arm) in done:
        continue
    if existing.get("total_cost_usd", 0) > 1.0:
        print("BUDGET EXCEEDED")
        break
    r = run_episode(scenario, diff, seed, arm)
    existing["episodes"].append(r)
    results_file.write_text(json.dumps(existing, indent=2, default=str), encoding="utf-8")

print(f"\n=== Done. Total cost: ${existing['total_cost_usd']:.4f} ===")
for e in existing["episodes"]:
    print(f"  {e['scenario']}/{e['arm']}: delta={e['score_delta']}, valid={e['n_valid_actions']}")
