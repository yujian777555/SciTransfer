"""G0: Secure model input builder with hidden-evaluator isolation.

This module provides the ONLY interface between the candidate agent/model
and the environment. It enforces a strict whitelist of candidate-safe fields
and prevents any hidden evaluator data from reaching the model.

Critical design:
- build_model_input() is the single entry point for model input
- Hidden fields (criticalHypotheses, criticalQuestions, associatedNotes) are NEVER included
- Canary markers can be injected to verify isolation
- No scorer API handle is accessible from candidate code
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Optional

# Hidden fields that MUST NEVER reach the candidate agent/model
HIDDEN_SCORER_FIELDS = {
    "criticalHypotheses",
    "criticalQuestions",
    "associatedNotes",
    "associatedUUIDs",
    "scoreCard",
    "gold_program",
    "gold_results",
    "eval_script",
}

# Canary marker prefix for leakage tests
CANARY_PREFIX = "CANARY_SECRET_"


@dataclass
class ModelInput:
    """Whitelisted model input. Contains ONLY candidate-safe fields."""
    task_description: str
    sanitized_observation: dict  # From CandidateAgent.observe()
    allowed_action_schema: list[str]  # List of valid action names
    recent_public_actions: list[dict]  # Recent actions and their public results
    step: int
    timestamp: float

    def to_model_message(self) -> str:
        """Serialize for model consumption. MUST NOT include hidden fields."""
        return json.dumps({
            "task_description": self.task_description,
            "observation": self.sanitized_observation,
            "allowed_actions": self.allowed_action_schema,
            "recent_actions": self.recent_public_actions,
            "step": self.step,
        }, ensure_ascii=False)

    def to_dict(self) -> dict:
        return {
            "task_description": self.task_description,
            "sanitized_observation": self.sanitized_observation,
            "allowed_action_schema": self.allowed_action_schema,
            "recent_public_actions": self.recent_public_actions,
            "step": self.step,
            "timestamp": self.timestamp,
        }


def build_model_input(
    safe_task_description: str,
    sanitized_observation: dict,
    allowed_action_schema: list[str],
    recent_public_actions: list[dict],
    step: int = 0,
) -> ModelInput:
    """Build whitelisted model input. This is the ONLY interface to the model.

    Guarantees:
    1. Only whitelisted fields are included
    2. Hidden scorer fields are stripped
    3. Canary markers are preserved for leakage testing
    """
    # Strip any hidden fields that might have leaked into observation
    clean_obs = _strip_hidden_fields(sanitized_observation)

    # Strip hidden fields from recent actions
    clean_actions = []
    for action in recent_public_actions:
        clean_actions.append(_strip_hidden_fields(action))

    return ModelInput(
        task_description=safe_task_description,
        sanitized_observation=clean_obs,
        allowed_action_schema=allowed_action_schema,
        recent_public_actions=clean_actions,
        step=step,
        timestamp=time.time(),
    )


def _strip_hidden_fields(data: Any) -> Any:
    """Recursively remove hidden scorer fields from data structure."""
    if isinstance(data, dict):
        return {
            k: _strip_hidden_fields(v)
            for k, v in data.items()
            if k not in HIDDEN_SCORER_FIELDS
        }
    elif isinstance(data, list):
        return [_strip_hidden_fields(item) for item in data]
    else:
        return data


def inject_canary_markers(scorer_data: dict, canary_id: str = "TEST") -> dict:
    """Inject canary markers into scorer-only fields for leakage testing.

    This is ONLY used in tests to verify isolation.
    """
    result = dict(scorer_data)
    for field_name in HIDDEN_SCORER_FIELDS:
        if field_name in result:
            marker = f"{CANARY_PREFIX}{canary_id}_{field_name}"
            if isinstance(result[field_name], list):
                result[field_name] = result[field_name] + [marker]
            elif isinstance(result[field_name], str):
                result[field_name] = result[field_name] + " " + marker
            else:
                result[field_name] = marker
    return result


def check_canary_leakage(data: Any, canary_id: str = "TEST") -> list[str]:
    """Check if any canary markers appear in the data. Returns list of leaked markers."""
    data_str = json.dumps(data, default=str)
    leaked = []
    for field_name in HIDDEN_SCORER_FIELDS:
        marker = f"{CANARY_PREFIX}{canary_id}_{field_name}"
        if marker in data_str:
            leaked.append(marker)
    return leaked


def get_safe_task_description(scorecard: dict) -> str:
    """Extract ONLY the task description from scorecard. Strip all hidden fields."""
    return scorecard.get("taskDescription", "")


def get_safe_observation_summary(obs: dict) -> dict:
    """Extract candidate-safe observation fields only."""
    return {
        "accessible_objects": obs.get("accessible_objects", []),
        "inventory": obs.get("inventory", []),
        "nearby_objects": obs.get("nearby_objects", []),
        "agent_location": obs.get("agent_location", ""),
        "last_action_message": obs.get("last_action_message", ""),
        "errors": obs.get("errors", []),
    }
