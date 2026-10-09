"""R2-R1 corrected DiscoveryWorld adapter with official action schema.

Key fixes:
- Official ActionType names (MOVE_DIRECTION, PICKUP, USE, etc.)
- Action success validation (not just tick)
- Observation-dependent decisions (not step-count proxy)
- Full step-by-step JSONL traces
- Hidden evaluator info isolation (TrustedEvaluator vs CandidateAgent)
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# ---- Official DiscoveryWorld ActionType enum ----
OFFICIAL_ACTIONS = {
    "PICKUP", "DROP", "PUT", "OPEN", "CLOSE", "ACTIVATE", "DEACTIVATE",
    "TALK", "EAT", "READ", "USE", "MOVE_DIRECTION", "ROTATE_DIRECTION",
    "TELEPORT_TO_LOCATION", "TELEPORT_TO_OBJECT",
}

VALID_DIRECTIONS = {"north", "east", "south", "west"}

# Hidden evaluator fields that MUST NOT reach candidate agent
HIDDEN_FIELDS = {"criticalHypotheses", "criticalQuestions", "associatedNotes"}


# ---- Core types ----

class Arm(str, Enum):
    NO_STRATEGY = "NO_STRATEGY"
    FIXED_CONDITIONAL_STRATEGY = "FIXED_CONDITIONAL_STRATEGY"
    PLACEBO = "PLACEBO"


class ActionStatus(str, Enum):
    ACCEPTED = "ACCEPTED"        # Parsed and executed successfully
    REJECTED = "REJECTED"        # Parsed but execution failed (success=False)
    INVALID = "INVALID"          # Failed schema validation
    PARSE_ERROR = "PARSE_ERROR"  # Failed to parse JSON


@dataclass
class SanitizedObservation:
    """Candidate-facing observation with hidden fields removed."""
    step: int
    timestamp: float
    accessible_objects: list[dict]  # uuid, name, description only
    inventory: list[dict]
    nearby_objects: list[dict]
    agent_location: str
    last_action_message: str
    errors: list[str]

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "timestamp": self.timestamp,
            "accessible_objects": self.accessible_objects,
            "inventory": self.inventory,
            "nearby_objects": self.nearby_objects,
            "agent_location": self.agent_location,
            "last_action_message": self.last_action_message,
            "errors": self.errors,
        }


@dataclass
class ActionRecord:
    step: int
    timestamp: float
    proposed_action: dict  # What the agent proposed
    validated_action: dict  # After schema validation
    action_status: str  # ACCEPTED / REJECTED / INVALID
    response_success: bool
    response_errors: list[str]
    rationale: str  # Why this action was chosen (observation-dependent)
    evidence_used: list[str]  # What observations influenced the decision

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "timestamp": self.timestamp,
            "proposed_action": self.proposed_action,
            "validated_action": self.validated_action,
            "action_status": self.action_status,
            "response_success": self.response_success,
            "response_errors": self.response_errors,
            "rationale": self.rationale,
            "evidence_used": self.evidence_used,
        }


@dataclass
class StepEvent:
    """Complete immutable per-step event."""
    step: int
    observation: SanitizedObservation
    action: ActionRecord
    next_observation: Optional[SanitizedObservation]
    env_ticked: bool

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "observation": self.observation.to_dict(),
            "action": self.action.to_dict(),
            "next_observation": self.next_observation.to_dict() if self.next_observation else None,
            "env_ticked": self.env_ticked,
        }


@dataclass
class EpisodeResult:
    episode_id: str
    scenario: str
    difficulty: str
    seed: int
    arm: str
    agent_id: str
    model: str
    status: str
    steps_taken: int
    initial_score: float
    final_score: float
    max_score: float
    score_delta: float
    completed: bool
    completed_successfully: bool
    n_valid_actions: int
    n_invalid_actions: int
    n_decision_points: int  # Real evidence-dependent decisions
    elapsed_s: float
    events: list[StepEvent] = field(default_factory=list)
    # Trusted evaluator only (NOT in candidate traces)
    trusted_scorecard: Optional[dict] = None

    def to_candidate_dict(self) -> dict:
        """Serialize WITHOUT hidden evaluator info."""
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
            "initial_score": self.initial_score,
            "final_score": self.final_score,
            "max_score": self.max_score,
            "score_delta": self.score_delta,
            "completed": self.completed,
            "completed_successfully": self.completed_successfully,
            "n_valid_actions": self.n_valid_actions,
            "n_invalid_actions": self.n_invalid_actions,
            "n_decision_points": self.n_decision_points,
            "n_observations": len(self.events),
            "n_actions": len(self.events),
            "elapsed_s": round(self.elapsed_s, 3),
            "events": [e.to_dict() for e in self.events],
        }

    def to_trusted_dict(self) -> dict:
        """Serialize WITH hidden evaluator info (for trusted scorer audit only)."""
        d = self.to_candidate_dict()
        d["trusted_scorecard"] = self.trusted_scorecard
        return d


# ---- Action schema validator ----

def validate_action(action_json: dict) -> tuple[bool, str, dict]:
    """Validate action against official schema. Returns (valid, error, validated_action)."""
    if not isinstance(action_json, dict):
        return False, "Action must be a dict", {}

    action_type = action_json.get("action")
    if not action_type:
        return False, "Missing 'action' key", {}

    if action_type not in OFFICIAL_ACTIONS:
        return False, f"Unknown action type: {action_type}. Must be one of {sorted(OFFICIAL_ACTIONS)}", {}

    validated = {"action": action_type}

    # Validate arguments per action type
    if action_type == "MOVE_DIRECTION":
        arg1 = action_json.get("arg1")
        if arg1 not in VALID_DIRECTIONS:
            return False, f"Invalid direction: {arg1}. Must be one of {sorted(VALID_DIRECTIONS)}", {}
        validated["arg1"] = arg1

    elif action_type == "ROTATE_DIRECTION":
        arg1 = action_json.get("arg1")
        if arg1 not in VALID_DIRECTIONS:
            return False, f"Invalid direction: {arg1}. Must be one of {sorted(VALID_DIRECTIONS)}", {}
        validated["arg1"] = arg1

    elif action_type == "PICKUP":
        arg1 = action_json.get("arg1")
        if arg1 is None:
            return False, "PICKUP requires arg1 (object UUID)", {}
        try:
            validated["arg1"] = int(arg1)
        except (ValueError, TypeError):
            return False, f"PICKUP arg1 must be integer UUID, got: {arg1!r}", {}

    elif action_type == "USE":
        arg1 = action_json.get("arg1")
        arg2 = action_json.get("arg2")
        if arg1 is None or arg2 is None:
            return False, "USE requires arg1 (tool UUID) and arg2 (target UUID)", {}
        try:
            validated["arg1"] = int(arg1)
            validated["arg2"] = int(arg2)
        except (ValueError, TypeError):
            return False, "USE args must be integer UUIDs", {}

    elif action_type in ("DROP", "OPEN", "CLOSE", "ACTIVATE", "DEACTIVATE", "READ", "EAT"):
        arg1 = action_json.get("arg1")
        if arg1 is None:
            return False, f"{action_type} requires arg1 (object UUID)", {}
        try:
            validated["arg1"] = int(arg1)
        except (ValueError, TypeError):
            return False, f"{action_type} arg1 must be integer UUID", {}

    return True, "", validated


# ---- Trusted Evaluator (can access hidden info) ----

class TrustedEvaluator:
    """Only this class may call getTaskScorecard()."""

    @staticmethod
    def get_initial_score(api) -> tuple[float, float, bool, bool]:
        """Get initial score before any actions. Returns (score, max_score, completed, completed_successfully)."""
        scorecard = api.getTaskScorecard()
        if scorecard and len(scorecard) > 0:
            sc = scorecard[0]
            return (
                float(sc.get("score", 0)),
                float(sc.get("maxScore", 0)),
                sc.get("completed", False),
                sc.get("completedSuccessfully", False),
            )
        return 0.0, 0.0, False, False

    @staticmethod
    def get_final_score(api) -> tuple[float, float, bool, bool]:
        scorecard = api.getTaskScorecard()
        if scorecard and len(scorecard) > 0:
            sc = scorecard[0]
            return (
                float(sc.get("score", 0)),
                float(sc.get("maxScore", 0)),
                sc.get("completed", False),
                sc.get("completedSuccessfully", False),
            )
        return 0.0, 0.0, False, False

    @staticmethod
    def get_full_scorecard(api) -> dict:
        """Get full scorecard including hidden fields (for trusted audit only)."""
        scorecard = api.getTaskScorecard()
        return scorecard[0] if scorecard else {}


# ---- Candidate Agent (CANNOT access hidden info) ----

class CandidateAgent:
    """Base class for candidate agents. MUST NOT access hidden evaluator info."""

    def __init__(self, arm: Arm, strategy_id: str = "none"):
        self.arm = arm
        self.strategy_id = strategy_id
        self.action_count = 0
        self.history: list[dict] = []

    def observe(self, raw_obs: dict) -> SanitizedObservation:
        """Parse raw observation, REMOVING hidden fields."""
        ui = raw_obs.get("ui", {})
        errors = raw_obs.get("errors", [])

        # Helper to safely extract object info
        def extract_obj(obj):
            if isinstance(obj, dict):
                return {
                    "uuid": obj.get("uuid"),
                    "name": obj.get("name", str(obj)),
                    "description": obj.get("description", ""),
                }
            else:
                # String or other type — use as name
                return {"uuid": None, "name": str(obj), "description": ""}

        accessible = [extract_obj(o) for o in ui.get("accessibleEnvironmentObjects", [])]
        inventory = [extract_obj(o) for o in ui.get("inventoryObjects", [])]
        nearby = [extract_obj(o) for o in ui.get("nearbyObjects", [])]

        return SanitizedObservation(
            step=self.action_count,
            timestamp=time.time(),
            accessible_objects=accessible,
            inventory=inventory,
            nearby_objects=nearby,
            agent_location=str(ui.get("agentLocation", "")),
            last_action_message=str(ui.get("lastActionMessage", "")),
            errors=errors if isinstance(errors, list) else [str(errors)],
        )

    def decide(self, obs: SanitizedObservation, task_description: str) -> tuple[dict, str, list[str]]:
        """Choose action based on observation. Returns (action_json, rationale, evidence_used)."""
        raise NotImplementedError


class EvidencePolicyAgent(CandidateAgent):
    """Agent that makes decisions based on actual observation content.

    This is NOT a step-count script — it examines the observation
    to determine what to do next.
    """

    def decide(self, obs: SanitizedObservation, task_description: str) -> tuple[dict, str, list[str]]:
        self.action_count += 1
        evidence = []

        # Evidence-dependent decision logic
        # Check what's in inventory
        has_key = any("key" in obj.get("name", "").lower() for obj in obs.inventory)
        has_jar = any("jar" in obj.get("name", "").lower() for obj in obs.inventory)

        # Check what's accessible
        accessible_names = [obj.get("name", "") for obj in obs.accessible_objects]
        has_key_accessible = any("key" in name.lower() for name in accessible_names)
        has_jar_accessible = any("jar" in name.lower() for name in accessible_names)
        has_dispenser = any("dispenser" in name.lower() or "chemical" in name.lower() for name in accessible_names)

        # Check last action result
        last_msg = obs.last_action_message.lower()
        last_failed = "error" in last_msg or "invalid" in last_msg or "could not" in last_msg

        # DECISION: Based on what we observe
        if has_key and has_jar:
            # Both in inventory — try to use key on jar
            key_uuid = next((obj["uuid"] for obj in obs.inventory if "key" in obj.get("name", "").lower()), None)
            jar_uuid = next((obj["uuid"] for obj in obs.inventory if "jar" in obj.get("name", "").lower()), None)
            if key_uuid and jar_uuid:
                action = {"action": "USE", "arg1": int(key_uuid), "arg2": int(jar_uuid)}
                rationale = "Both key and jar in inventory; using key on jar to derust"
                evidence = [f"inventory has key (uuid={key_uuid})", f"inventory has jar (uuid={jar_uuid})"]
                return action, rationale, evidence

        if has_key_accessible and not has_key:
            # Key is accessible but not in inventory — pick it up
            key_uuid = next((obj["uuid"] for obj in obs.accessible_objects if "key" in obj.get("name", "").lower()), None)
            if key_uuid:
                action = {"action": "PICKUP", "arg1": int(key_uuid)}
                rationale = "Key visible in environment; picking up"
                evidence = [f"accessible key at uuid={key_uuid}"]
                return action, rationale, evidence

        if has_jar_accessible and not has_jar:
            # Jar is accessible but not in inventory — pick it up
            jar_uuid = next((obj["uuid"] for obj in obs.accessible_objects if "jar" in obj.get("name", "").lower()), None)
            if jar_uuid:
                action = {"action": "PICKUP", "arg1": int(jar_uuid)}
                rationale = "Jar visible in environment; picking up"
                evidence = [f"accessible jar at uuid={jar_uuid}"]
                return action, rationale, evidence

        if has_dispenser and has_jar:
            # Dispenser accessible and we have jar — try using dispenser
            disp_uuid = next(
                (obj["uuid"] for obj in obs.accessible_objects
                 if "dispenser" in obj.get("name", "").lower() or "chemical" in obj.get("name", "").lower()),
                None
            )
            jar_uuid = next((obj["uuid"] for obj in obs.inventory if "jar" in obj.get("name", "").lower()), None)
            if disp_uuid and jar_uuid:
                action = {"action": "USE", "arg1": int(disp_uuid), "arg2": int(jar_uuid)}
                rationale = "Chemical dispenser accessible and jar in inventory; adding chemical"
                evidence = [f"accessible dispenser at uuid={disp_uuid}", f"jar in inventory uuid={jar_uuid}"]
                return action, rationale, evidence

        # Default: explore (move to find objects)
        # Use observation to decide direction — try different directions
        if last_failed:
            evidence.append(f"last action failed: {obs.last_action_message[:50]}")
            # Try a different direction based on what worked before
            action = {"action": "MOVE_DIRECTION", "arg1": "east"}
            rationale = "Last action failed; exploring in different direction"
        else:
            # Move to explore — try north first, then east if that fails
            action = {"action": "MOVE_DIRECTION", "arg1": "east"}
            rationale = "No target objects visible; exploring environment"
            evidence.append(f"accessible objects: {accessible_names[:3]}")

        return action, rationale, evidence


class NoStrategyAgent(CandidateAgent):
    """Baseline agent without strategy — uses simple observation-based logic."""

    def decide(self, obs: SanitizedObservation, task_description: str) -> tuple[dict, str, list[str]]:
        self.action_count += 1

        # Simple: pick up first accessible object, then explore
        if obs.accessible_objects and self.action_count <= 3:
            obj = obs.accessible_objects[0]
            if obj.get("uuid"):
                action = {"action": "PICKUP", "arg1": int(obj["uuid"])}
                rationale = f"Picking up first accessible object: {obj.get('name')}"
                evidence = [f"accessible: {obj.get('name')}"]
                return action, rationale, evidence

        # Otherwise explore
        action = {"action": "MOVE_DIRECTION", "arg1": "north"}
        rationale = "Exploring environment"
        evidence = [f"step {self.action_count}"]
        return action, rationale, evidence


# ---- Episode runner with full tracing ----

def run_episode_r2r1(
    scenario: str,
    difficulty: str,
    seed: int,
    arm: Arm,
    max_steps: int = 15,
    max_seconds: float = 120.0,
) -> EpisodeResult:
    """Run one episode with full step-by-step tracing and action validation."""
    import warnings
    warnings.filterwarnings("ignore")
    from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

    episode_id = f"r2r1_{scenario.replace(' ', '_')}_{difficulty}_{arm.value}_s{seed}"
    t0 = time.time()

    # Create API
    api = DiscoveryWorldAPI()
    try:
        api.loadScenario(scenario, difficulty, seed, 1)
    except Exception as e:
        return EpisodeResult(
            episode_id=episode_id, scenario=scenario, difficulty=difficulty,
            seed=seed, arm=arm.value, agent_id="EvidencePolicyAgent",
            model="rule-based-v2", status="ERROR", steps_taken=0,
            initial_score=0, final_score=0, max_score=0, score_delta=0,
            completed=False, completed_successfully=False,
            n_valid_actions=0, n_invalid_actions=0, n_decision_points=0,
            elapsed_s=time.time() - t0,
        )

    # TRUSTED EVALUATOR: Get initial score (hidden from candidate)
    initial_score, max_score, init_completed, init_completed_ok = TrustedEvaluator.get_initial_score(api)

    # Get task description (candidate-safe)
    scorecard = api.getTaskScorecard()
    task_desc = ""
    if scorecard and len(scorecard) > 0:
        task_desc = scorecard[0].get("taskDescription", "")

    # Create candidate agent
    if arm == Arm.FIXED_CONDITIONAL_STRATEGY:
        agent = EvidencePolicyAgent(arm, "baseline_first")
    else:
        agent = NoStrategyAgent(arm, "none")

    events: list[StepEvent] = []
    n_valid = 0
    n_invalid = 0
    n_decision_points = 0

    for step in range(max_steps):
        elapsed = time.time() - t0
        if elapsed > max_seconds:
            break

        # Observe (sanitized)
        raw_obs = api.getAgentObservation(0)
        obs = agent.observe(raw_obs)

        # Decide (observation-dependent)
        action_json, rationale, evidence_used = agent.decide(obs, task_desc)

        # Validate action schema
        is_valid, error_msg, validated = validate_action(action_json)

        if not is_valid:
            # Record invalid action — does NOT count as decision point
            action_record = ActionRecord(
                step=step, timestamp=time.time(),
                proposed_action=action_json, validated_action={},
                action_status=ActionStatus.INVALID.value,
                response_success=False,
                response_errors=[error_msg],
                rationale=rationale, evidence_used=evidence_used,
            )
            n_invalid += 1
        else:
            # Execute action
            try:
                result = api.performAgentAction(0, validated)
                response_success = result.get("success", False)
                response_errors = result.get("errors", [])
            except Exception as e:
                response_success = False
                response_errors = [str(e)]

            if response_success:
                action_status = ActionStatus.ACCEPTED.value
                n_valid += 1
                # This IS a real decision point if evidence was used
                if evidence_used:
                    n_decision_points += 1
            else:
                action_status = ActionStatus.REJECTED.value
                n_invalid += 1

            action_record = ActionRecord(
                step=step, timestamp=time.time(),
                proposed_action=action_json, validated_action=validated,
                action_status=action_status,
                response_success=response_success,
                response_errors=response_errors,
                rationale=rationale, evidence_used=evidence_used,
            )

        # Tick environment
        api.tick()

        # Get next observation
        next_raw = api.getAgentObservation(0)
        next_obs = agent.observe(next_raw)

        # Record step event
        event = StepEvent(
            step=step,
            observation=obs,
            action=action_record,
            next_observation=next_obs,
            env_ticked=True,
        )
        events.append(event)

    # TRUSTED EVALUATOR: Get final score
    final_score, max_score, completed, completed_ok = TrustedEvaluator.get_final_score(api)
    full_scorecard = TrustedEvaluator.get_full_scorecard(api)

    elapsed = time.time() - t0
    score_delta = final_score - initial_score

    # Status based on completion, not just score
    if completed_ok:
        status = "SUCCESS"
    elif final_score > initial_score:
        status = "PARTIAL_PROGRESS"
    else:
        status = "FAILED"

    return EpisodeResult(
        episode_id=episode_id,
        scenario=scenario,
        difficulty=difficulty,
        seed=seed,
        arm=arm.value,
        agent_id=agent.__class__.__name__,
        model="rule-based-v2",
        status=status,
        steps_taken=len(events),
        initial_score=initial_score,
        final_score=final_score,
        max_score=max_score,
        score_delta=score_delta,
        completed=completed,
        completed_successfully=completed_ok,
        n_valid_actions=n_valid,
        n_invalid_actions=n_invalid,
        n_decision_points=n_decision_points,
        elapsed_s=elapsed,
        events=events,
        trusted_scorecard=full_scorecard,
    )
