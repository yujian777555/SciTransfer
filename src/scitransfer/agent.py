"""Pinned agent harness: direct prompting with DeepSeek (OpenAI-compatible API).

Produces a self-contained Python program per ScienceAgentBench task.
Arm A gets the task only; Arm B gets the task plus a preregistered strategy block.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .core.types import (
    Arm,
    Budget,
    ScientificStrategy,
    sha256_of,
    stable_json,
)

# ---- Prompts (derived from official ScienceAgentBench agent.py) ----

SYSTEM_PROMPT = (
    "You are an expert Python programming assistant that helps scientist users "
    "to write high-quality code to solve their tasks.\n"
    "Given a user request, you are expected to write a complete program that "
    "accomplishes the requested task and save any outputs in the correct format.\n"
    "Please wrap your program in a code block that specifies the script type, python. For example:\n"
    "```python\nprint(\"Hello World!\")\n```"
)

FORMAT_PROMPT = (
    "Please keep your response concise and do not use a code block if it's not intended to be executed.\n"
    "Please do not suggest a few line changes, incomplete program outline, or partial code that requires the user to modify.\n"
    "Please do not use any interactive Python commands in your program, such as `!pip install numpy`, "
    "which will cause execution errors."
)

REQUEST_PROMPT = "Here's the user request you need to work on:"

DATA_INFO_PROMPT = (
    "You can access the dataset at `{dataset_path}`. Here is the directory structure of the dataset:\n"
    "```\n{dataset_folder_tree}\n```\n"
    "Here are some helpful previews for the dataset file(s):\n"
    "{dataset_preview}"
)

# Preregistered fixed strategy for Arm B — generic tactic, NOT a solution hint.
FIXED_STRATEGY = ScientificStrategy(
    strategy_id="baseline_first_validation_v1",
    preconditions=(
        "The task asks for a data-driven scientific analysis with a specific output file."
    ),
    research_action=(
        "Before writing the full analysis, first write a minimal baseline that only loads "
        "the data and saves a trivial but correctly formatted output at the required path. "
        "Then iterate: add one analysis step at a time and re-run to verify each step produces "
        "a valid intermediate result before adding the next. Prefer the cheapest discriminating "
        "check over a complex pipeline."
    ),
    expected_evidence=(
        "The program must save the output file at the exact requested path, and each iteration "
        "must be re-executed to confirm no runtime error before proceeding."
    ),
    invalidity_conditions=(
        "If the dataset path is inaccessible or the required output format is ambiguous after "
        "inspecting previews, stop and report the blocker rather than inventing data."
    ),
    source_provenance=(
        "Preregistered generic research tactic (baseline-before-escalation); "
        "no target-task outcome observed; no hidden evaluation key used."
    ),
    cost_constraints="Stay within the run budget; do not add unnecessary dependencies.",
)

PLACEBO_TEXT = (
    "[NEUTRAL CONTEXT]\n"
    "Please proceed carefully with the programming task below.\n"
    "[END NEUTRAL CONTEXT]"
)


@dataclass
class AgentResponse:
    text: str
    program: Optional[str]
    prompt: str
    prompt_hash: str
    strategy_id: Optional[str]
    strategy_hash: Optional[str]
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    error: Optional[str] = None


def build_prompt(
    task_dict: dict[str, Any],
    arm: Arm,
    strategy: Optional[ScientificStrategy] = None,
    dataset_path: str = "benchmark/datasets",
) -> tuple[str, Optional[str], Optional[str]]:
    """Return (prompt, strategy_id, strategy_hash)."""
    sys_msg = SYSTEM_PROMPT + "\n\n" + FORMAT_PROMPT + "\n\n" + REQUEST_PROMPT
    sys_msg += "\n" + task_dict["task_inst"]
    sys_msg += "\n" + DATA_INFO_PROMPT.format(
        dataset_path=dataset_path,
        dataset_folder_tree=task_dict["dataset_folder_tree"],
        dataset_preview=task_dict["dataset_preview"],
    )

    strategy_id = None
    strategy_hash = None
    if arm == Arm.FIXED_STRATEGY:
        strat = strategy or FIXED_STRATEGY
        block = strat.prompt_block()
        sys_msg = block + "\n\n" + sys_msg
        strategy_id = strat.strategy_id
        strategy_hash = sha256_of(stable_json(strat.to_dict()))
    elif arm == Arm.PLACEBO:
        sys_msg = PLACEBO_TEXT + "\n\n" + sys_msg

    return sys_msg, strategy_id, strategy_hash


def extract_python_program(text: str) -> Optional[str]:
    match = re.search(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: any fenced block
    match = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


# Rough per-1M-token prices (USD) used for cost accounting; documented in audit.
MODEL_PRICES_USD_PER_1M = {
    "deepseek-v4-pro": {"input": 0.5, "output": 1.5},
    "deepseek-flash": {"input": 0.1, "output": 0.3},
    "deepseek-chat": {"input": 0.5, "output": 1.5},
}


def _estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    prices = MODEL_PRICES_USD_PER_1M.get(model, {"input": 0.5, "output": 1.5})
    return (tokens_in * prices["input"] + tokens_out * prices["output"]) / 1e6


def call_deepseek(
    prompt: str,
    model: str = "deepseek-v4-pro",
    api_key: Optional[str] = None,
    max_tokens: int = 8192,
    temperature: float = 0.0,
    timeout_s: int = 300,
    base_url: str = "https://api.deepseek.com/v1",
) -> AgentResponse:
    """Call DeepSeek chat completions (OpenAI-compatible). Fail-closed on errors."""
    key = api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        return AgentResponse(
            text="", program=None, prompt=prompt, prompt_hash=sha256_of(prompt),
            strategy_id=None, strategy_hash=None, model=model,
            tokens_in=0, tokens_out=0, cost_usd=0.0,
            error="No API key available (DEEPSEEK_API_KEY / OPENAI_API_KEY).",
        )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:
            resp = json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        return AgentResponse(
            text="", program=None, prompt=prompt, prompt_hash=sha256_of(prompt),
            strategy_id=None, strategy_hash=None, model=model,
            tokens_in=0, tokens_out=0, cost_usd=0.0,
            error=f"HTTP {e.code}: {body}",
        )
    except Exception as e:
        return AgentResponse(
            text="", program=None, prompt=prompt, prompt_hash=sha256_of(prompt),
            strategy_id=None, strategy_hash=None, model=model,
            tokens_in=0, tokens_out=0, cost_usd=0.0,
            error=f"{type(e).__name__}: {e}",
        )

    text = ""
    try:
        text = resp["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError):
        return AgentResponse(
            text="", program=None, prompt=prompt, prompt_hash=sha256_of(prompt),
            strategy_id=None, strategy_hash=None, model=model,
            tokens_in=0, tokens_out=0, cost_usd=0.0,
            error=f"Malformed API response: {stable_json(resp)[:300]}",
        )

    usage = resp.get("usage", {})
    tokens_in = int(usage.get("prompt_tokens", 0))
    tokens_out = int(usage.get("completion_tokens", 0))
    cost = _estimate_cost(model, tokens_in, tokens_out)
    program = extract_python_program(text)

    return AgentResponse(
        text=text,
        program=program,
        prompt=prompt,
        prompt_hash=sha256_of(prompt),
        strategy_id=None,
        strategy_hash=None,
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=round(cost, 6),
        error=None if program else "No python code block found in model response.",
    )
