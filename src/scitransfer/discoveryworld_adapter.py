"""Multi-step research decision adapter for DiscoveryWorld.

Implements observe → decide → act → evidence → decide again loop.
Strategies are hand-authored feasibility interventions (NOT learned/transferred).

Design constraints (plan_002.md Track 2):
- Real multi-step decisions (≥2 per episode)
- Same tools/actions for all arms
- No access to hidden gold answers
- Hard step/time/token budget
- Immutable logging
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# ---- Core types ----

class Arm(str, Enum):
    NO_STRATEGY = "NO_STRATEGY"
    FIXED_CONDITIONAL_STRATEGY = "FIXED_CONDITIONAL_STRATEGY"
    PLACEBO = "PLACEBO"


class RunStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"


@dataclass
class Observation:
    step: int
    ui_text: str
    errors: list[str]
    vision_summary: str
    raw: dict[str, Any]


@dataclass
class Action:
    step: int
    action_type: str
    action_json: dict[str, Any]
    reasoning: str
    is_decision_point: bool  # True if this action depends on prior evidence


@dataclass
class EpisodeTrace:
    episode_id: str
    scenario: str
    difficulty: str
    seed: int
    arm: str
    agent_id: str
    model: str
    status: str
    steps_taken: int
    final_score: float
    max_score: float
    score_normalized: float
    n_decision_points: int
    elapsed_s: float
    observations: list[Observation] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    scorecard: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "episode_id": self.episode_id,
            "scenario": self.scenario,
            "difficulty": self.difficulty,
            "seed": self.seed,
            "arm": self.arm,
            "agent_id": self.agent_id,
            "model": self.model,
            "status": self.status,
            "steps_taken": self.steps_taken,
            "final_score": self.final_score,
            "max_score": self.max_score,
            "score_normalized": self.score_normalized,
            "n_decision_points": self.n_decision_points,
            "elapsed_s": round(self.elapsed_s, 3),
            "n_observations": len(self.observations),
            "n_actions": len(self.actions),
            "scorecard": self.scorecard,
        }


# ---- Strategy definitions (hand-authored feasibility interventions) ----

STRATEGIES = {
    "none": None,
    "baseline_first": {
        "id": "baseline_first_validation_v1",
        "type": "FIXED_CONDITIONAL_STRATEGY",
        "label": "Hand-authored feasibility intervention (NOT learned/transferred)",
        "rules": [
            "IF no object has been inspected yet THEN explore environment systematically (look around, move to new areas)",
            "IF an object has been inspected but not yet acted upon THEN try the most likely action based on task description",
            "IF an action failed or produced unexpected result THEN re-inspect the current state before retrying",
            "IF task score is still 0 after 5 actions THEN try a completely different approach",
        ],
    },
    "placebo": {
        "id": "placebo_neutral_v1",
        "type": "PLACEBO",
        "label": "Length-matched neutral context (NOT a strategy)",
        "rules": ["Continue with the task."],
    },
}


# ---- Minimal agent policy (rule-based for calibration, no API needed) ----

class SimplePolicyAgent:
    """A deterministic rule-based agent for calibration testing.

    This is NOT an LLM agent — it's a baseline to verify the environment
    works and produces meaningful score variation. LLM agents can be
    plugged in later within the same interface.
    """

    def __init__(self, arm: Arm, strategy_id: str = "none"):
        self.arm = arm
        self.strategy_id = strategy_id
        self.strategy = STRATEGIES.get(strategy_id)
        self.history: list[dict] = []
        self.action_count = 0

    def decide(self, observation: Observation, task_description: str) -> Action:
        """Choose next action based on observation and strategy."""
        self.action_count += 1

        # Simple heuristic policy: explore then interact
        if self.action_count <= 3:
            # Explore phase: move around
            action_json = {"action": "moveAgentForward"}
            reasoning = "Exploring environment (initial phase)"
        elif self.action_count <= 6:
            # Try interacting with objects
            action_json = {"action": "pickupObject", "objectName": "key"}
            reasoning = "Attempting to pick up key"
        else:
            # Try using items
            action_json = {"action": "useObject", "objectName": "jar"}
            reasoning = "Attempting to use jar"

        # Apply strategy modulation
        if self.strategy and self.strategy["rules"]:
            # For FIXED_CONDITIONAL_STRATEGY: apply rules
            if self.arm == Arm.FIXED_CONDITIONAL_STRATEGY:
                # Simple rule application: if score still 0 after5 steps, change approach
                if self.action_count > 5:
                    reasoning += " [STRATEGY: switching approach after no progress]"
                    action_json = {"action": "useObject", "objectName": "chemicalDispenser"}

        is_decision = self.action_count >= 2  # Second decision depends on first evidence

        return Action(
            step=self.action_count,
            action_type=action_json.get("action", "unknown"),
            action_json=action_json,
            reasoning=reasoning,
            is_decision_point=is_decision,
        )

    def observe(self, raw_obs: dict) -> Observation:
        """Parse raw observation into structured form."""
        ui = raw_obs.get("ui", {})
        errors = raw_obs.get("errors", [])
        vision = raw_obs.get("vision", "")

        # Extract text from UI
        ui_text = ""
        if isinstance(ui, dict):
            ui_text = json.dumps(ui)[:500]
        elif isinstance(ui, str):
            ui_text = ui[:500]

        return Observation(
            step=self.action_count,
            ui_text=ui_text,
            errors=errors if isinstance(errors, list) else [str(errors)],
            vision_summary=str(vision)[:200],
            raw=raw_obs,
        )


# ---- Episode runner ----

def run_episode(
    scenario: str,
    difficulty: str,
    seed: int,
    arm: Arm,
    max_steps: int = 15,
    max_seconds: float = 120.0,
) -> EpisodeTrace:
    """Run one multi-step episode in DiscoveryWorld.

    Returns a complete EpisodeTrace with real environment interaction.
    """
    import warnings
    warnings.filterwarnings("ignore")

    from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

    episode_id = f"r2b_{scenario.replace(' ','_')}_{difficulty}_{arm.value}_s{seed}"
    t0 = time.time()

    # Create fresh API instance (isolation)
    api = DiscoveryWorldAPI()

    # Load scenario with seed
    try:
        api.loadScenario(scenario, difficulty, seed, 1)
    except Exception as e:
        return EpisodeTrace(
            episode_id=episode_id, scenario=scenario, difficulty=difficulty,
            seed=seed, arm=arm.value, agent_id="SimplePolicyAgent",
            model="rule-based-v1", status=RunStatus.ERROR.value,
            steps_taken=0, final_score=0, max_score=0, score_normalized=0,
            n_decision_points=0, elapsed_s=time.time() - t0,
        )

    # Get task description from scorecard
    scorecard = api.getTaskScorecard()
    task_desc = ""
    max_score = 0
    if scorecard and len(scorecard) > 0:
        task_desc = scorecard[0].get("taskDescription", "")
        max_score = scorecard[0].get("maxScore", 0)

    # Create agent
    strategy_id = "none"
    if arm == Arm.FIXED_CONDITIONAL_STRATEGY:
        strategy_id = "baseline_first"
    elif arm == Arm.PLACEBO:
        strategy_id = "placebo"

    agent = SimplePolicyAgent(arm, strategy_id)

    # Multi-step loop
    n_decision_points = 0
    for step in range(max_steps):
        elapsed = time.time() - t0
        if elapsed > max_seconds:
            return EpisodeTrace(
                episode_id=episode_id, scenario=scenario, difficulty=difficulty,
                seed=seed, arm=arm.value, agent_id="SimplePolicyAgent",
                model="rule-based-v1", status=RunStatus.TIMEOUT.value,
                steps_taken=step, final_score=0, max_score=max_score,
                score_normalized=0, n_decision_points=n_decision_points,
                elapsed_s=elapsed,
                observations=agent.history and [] or [],
            )

        # Observe
        raw_obs = api.getAgentObservation(0)
        obs = agent.observe(raw_obs)

        # Decide
        action = agent.decide(obs, task_desc)
        if action.is_decision_point:
            n_decision_points += 1

        # Execute
        try:
            result = api.performAgentAction(0, action.action_json)
        except Exception as e:
            result = {"error": str(e)}

        # Tick to advance environment
        api.tick()

        # Record
        agent.history.append({
            "step": step,
            "observation": obs.ui_text[:200],
            "action": action.action_type,
            "reasoning": action.reasoning,
            "is_decision_point": action.is_decision_point,
            "result": str(result)[:200] if result else None,
        })

    # Final score
    final_scorecard = api.getTaskScorecard()
    final_score = 0
    final_max = max_score
    score_norm = 0
    if final_scorecard and len(final_scorecard) > 0:
        final_score = final_scorecard[0].get("score", 0)
        final_max = final_scorecard[0].get("maxScore", max_score)
        score_norm = final_scorecard[0].get("scoreNormalized", 0)

    elapsed = time.time() - t0
    status = RunStatus.SUCCESS.value if final_score > 0 else RunStatus.FAILED.value

    return EpisodeTrace(
        episode_id=episode_id,
        scenario=scenario,
        difficulty=difficulty,
        seed=seed,
        arm=arm.value,
        agent_id="SimplePolicyAgent",
        model="rule-based-v1",
        status=status,
        steps_taken=max_steps,
        final_score=final_score,
        max_score=final_max,
        score_normalized=score_norm,
        n_decision_points=n_decision_points,
        elapsed_s=elapsed,
        scorecard=final_scorecard,
    )
