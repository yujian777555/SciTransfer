"""G0 tests: hidden evaluator isolation and canary leakage detection."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.secure_input import (
    CANARY_PREFIX,
    HIDDEN_SCORER_FIELDS,
    build_model_input,
    check_canary_leakage,
    get_safe_observation_summary,
    get_safe_task_description,
    inject_canary_markers,
    _strip_hidden_fields,
)


# ---- Hidden field stripping ----

def test_strip_hidden_fields_removes_critical():
    data = {
        "taskDescription": "do something",
        "criticalHypotheses": ["SECRET"],
        "criticalQuestions": ["SECRET_Q"],
        "associatedNotes": "SECRET_NOTE",
        "safe_field": "visible",
    }
    cleaned = _strip_hidden_fields(data)
    assert "criticalHypotheses" not in cleaned
    assert "criticalQuestions" not in cleaned
    assert "associatedNotes" not in cleaned
    assert cleaned["safe_field"] == "visible"
    assert cleaned["taskDescription"] == "do something"


def test_strip_hidden_fields_recursive():
    data = {
        "outer": {
            "inner": {"criticalHypotheses": "SECRET", "safe": "ok"},
            "criticalQuestions": "SECRET",
        },
        "criticalHypotheses": "SECRET",
    }
    cleaned = _strip_hidden_fields(data)
    assert "criticalHypotheses" not in cleaned
    assert "criticalHypotheses" not in cleaned["outer"]
    assert "criticalHypotheses" not in cleaned["outer"]["inner"]
    assert cleaned["outer"]["inner"]["safe"] == "ok"


# ---- build_model_input whitelist ----

def test_build_model_input_strips_hidden():
    obs = {
        "accessible_objects": [{"uuid": 1, "name": "key"}],
        "inventory": [],
        "criticalHypotheses": ["SECRET"],
        "criticalQuestions": ["SECRET_Q"],
    }
    model_input = build_model_input(
        safe_task_description="test task",
        sanitized_observation=obs,
        allowed_action_schema=["MOVE_DIRECTION", "PICKUP"],
        recent_public_actions=[{"action": "MOVE_DIRECTION", "success": True, "criticalHypotheses": "SECRET"}],
    )
    d = model_input.to_dict()
    assert "criticalHypotheses" not in str(d)
    assert "criticalQuestions" not in str(d)
    assert "SECRET" not in str(d)


def test_build_model_input_message_clean():
    obs = {"accessible_objects": [], "criticalHypotheses": "CANARY_SECRET_TEST_criticalHypotheses"}
    model_input = build_model_input(
        safe_task_description="task",
        sanitized_observation=obs,
        allowed_action_schema=["USE"],
        recent_public_actions=[],
    )
    msg = model_input.to_model_message()
    assert "criticalHypotheses" not in msg
    assert "CANARY_SECRET" not in msg


# ---- Canary injection and detection ----

def test_canary_injection_and_detection():
    scorer_data = {
        "taskDescription": "safe",
        "criticalHypotheses": ["original"],
        "criticalQuestions": ["original_q"],
    }
    injected = inject_canary_markers(scorer_data, canary_id="TEST")
    assert f"{CANARY_PREFIX}TEST_criticalHypotheses" in str(injected["criticalHypotheses"])

    # Build model input from injected data
    model_input = build_model_input(
        safe_task_description="task",
        sanitized_observation={"accessible_objects": [], **injected},
        allowed_action_schema=["USE"],
        recent_public_actions=[],
    )
    d = model_input.to_dict()
    leaked = check_canary_leakage(d, canary_id="TEST")
    assert len(leaked) == 0, f"Canary leakage detected: {leaked}"


def test_canary_detection_finds_leak():
    """If hidden data DOES leak, canary detection must find it."""
    data = {
        "task": "safe",
        "criticalHypotheses": f"{CANARY_PREFIX}TEST_criticalHypotheses",
    }
    leaked = check_canary_leakage(data, canary_id="TEST")
    assert len(leaked) > 0, "Canary detection should find leaked marker"


# ---- Safe observation summary ----

def test_safe_observation_excludes_hidden():
    obs = {
        "accessible_objects": [{"uuid": 1}],
        "inventory": [],
        "nearby_objects": [],
        "agent_location": "room",
        "last_action_message": "moved",
        "errors": [],
        "criticalHypotheses": "SECRET",
    }
    safe = get_safe_observation_summary(obs)
    assert "criticalHypotheses" not in safe
    assert safe["agent_location"] == "room"


def test_safe_task_description_only():
    scorecard = {
        "taskDescription": "do the thing",
        "criticalHypotheses": ["SECRET"],
        "criticalQuestions": ["SECRET_Q"],
    }
    desc = get_safe_task_description(scorecard)
    assert desc == "do the thing"
    assert "SECRET" not in desc


# ---- Integration: full model message isolation ----

def test_full_model_message_no_hidden_fields():
    """End-to-end: build model input from realistic observation with hidden data."""
    raw_obs = {
        "ui": {
            "accessibleEnvironmentObjects": [{"uuid": "123", "name": "key", "description": "a key"}],
            "inventoryObjects": [],
            "nearbyObjects": [],
            "agentLocation": "shed",
            "lastActionMessage": "",
        },
        "errors": [],
        "criticalHypotheses": ["If X then Y"],
        "criticalQuestions": ["Is it Z?"],
    }

    # Sanitize observation (simulating CandidateAgent.observe)
    safe_obs = {
        "accessible_objects": [{"uuid": "123", "name": "key", "description": "a key"}],
        "inventory": [],
        "nearby_objects": [],
        "agent_location": "shed",
        "last_action_message": "",
        "errors": [],
    }

    model_input = build_model_input(
        safe_task_description="Find the rust remover",
        sanitized_observation=safe_obs,
        allowed_action_schema=["MOVE_DIRECTION", "PICKUP", "USE"],
        recent_public_actions=[],
        step=0,
    )

    msg = model_input.to_model_message()
    assert "criticalHypotheses" not in msg
    assert "criticalQuestions" not in msg
    assert "If X then Y" not in msg
    assert "Is it Z?" not in msg
    assert "key" in msg  # safe content IS present


# ---- Gitignore verification ----

def test_gitignore_blocks_trusted_files():
    """.gitignore must contain rules for trusted files."""
    gitignore = Path(__file__).resolve().parents[1] / ".gitignore"
    content = gitignore.read_text(encoding="utf-8")
    assert "*_trusted.json" in content
    assert "*trusted*.json" in content
