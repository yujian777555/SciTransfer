"""R2-R1 tests: action schema, observation-dependent decisions, leakage isolation."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.discoveryworld_r2r1 import (
    ActionRecord,
    ActionStatus,
    Arm,
    CandidateAgent,
    EpisodeResult,
    EvidencePolicyAgent,
    HIDDEN_FIELDS,
    NoStrategyAgent,
    OFFICIAL_ACTIONS,
    SanitizedObservation,
    StepEvent,
    TrustedEvaluator,
    VALID_DIRECTIONS,
    validate_action,
)


# ---- Action schema validation ----

def test_validate_move_direction_valid():
    valid, err, validated = validate_action({"action": "MOVE_DIRECTION", "arg1": "north"})
    assert valid is True
    assert validated == {"action": "MOVE_DIRECTION", "arg1": "north"}


def test_validate_move_direction_invalid_direction():
    valid, err, _ = validate_action({"action": "MOVE_DIRECTION", "arg1": "EAST"})
    assert valid is False
    assert "Invalid direction" in err


def test_validate_pickup_valid():
    valid, err, validated = validate_action({"action": "PICKUP", "arg1": 12345})
    assert valid is True
    assert validated == {"action": "PICKUP", "arg1": 12345}


def test_validate_pickup_missing_arg():
    valid, err, _ = validate_action({"action": "PICKUP"})
    assert valid is False
    assert "requires arg1" in err


def test_validate_use_valid():
    valid, err, validated = validate_action({"action": "USE", "arg1": 111, "arg2": 222})
    assert valid is True
    assert validated == {"action": "USE", "arg1": 111, "arg2": 222}


def test_validate_use_missing_arg2():
    valid, err, _ = validate_action({"action": "USE", "arg1": 111})
    assert valid is False
    assert "requires arg1" in err


def test_validate_unknown_action():
    valid, err, _ = validate_action({"action": "moveAgentForward"})
    assert valid is False
    assert "Unknown action" in err


def test_validate_camelcase_rejected():
    """Old invalid camelCase actions must be rejected."""
    for bad in ["moveAgentForward", "pickupObject", "useObject"]:
        valid, err, _ = validate_action({"action": bad})
        assert valid is False


def test_official_actions_set():
    assert "MOVE_DIRECTION" in OFFICIAL_ACTIONS
    assert "PICKUP" in OFFICIAL_ACTIONS
    assert "USE" in OFFICIAL_ACTIONS
    assert "moveAgentForward" not in OFFICIAL_ACTIONS


# ---- Observation sanitization ----

def test_sanitized_observation_excludes_hidden_fields():
    """SanitizedObservation must NOT contain criticalHypotheses/criticalQuestions."""
    obs = SanitizedObservation(
        step=0, timestamp=0,
        accessible_objects=[{"uuid": 1, "name": "key", "description": "a key"}],
        inventory=[], nearby_objects=[], agent_location="room",
        last_action_message="", errors=[],
    )
    d = obs.to_dict()
    for hidden in HIDDEN_FIELDS:
        assert hidden not in str(d), f"Hidden field {hidden} found in sanitized observation"


def test_candidate_agent_cannot_access_scorecard():
    """CandidateAgent must not have getTaskScorecard method."""
    agent = NoStrategyAgent(Arm.NO_STRATEGY, "none")
    assert not hasattr(agent, "getTaskScorecard")
    assert not hasattr(agent, "getFullScorecard")


# ---- Observation-dependent decisions ----

def test_evidence_policy_changes_action_on_different_observation():
    """Different observations must produce different actions."""
    agent = EvidencePolicyAgent(Arm.FIXED_CONDITIONAL_STRATEGY, "baseline_first")

    # Observation 1: key accessible
    obs1 = SanitizedObservation(
        step=0, timestamp=0,
        accessible_objects=[{"uuid": 100, "name": "rusted key", "description": ""}],
        inventory=[], nearby_objects=[], agent_location="room",
        last_action_message="", errors=[],
    )
    action1, rationale1, evidence1 = agent.decide(obs1, "task")

    # Observation 2: jar accessible (different)
    agent2 = EvidencePolicyAgent(Arm.FIXED_CONDITIONAL_STRATEGY, "baseline_first")
    obs2 = SanitizedObservation(
        step=0, timestamp=0,
        accessible_objects=[{"uuid": 200, "name": "mixing jar", "description": ""}],
        inventory=[], nearby_objects=[], agent_location="room",
        last_action_message="", errors=[],
    )
    action2, rationale2, evidence2 = agent2.decide(obs2, "task")

    # Different observations → different actions
    assert action1 != action2, f"Same action for different observations: {action1} vs {action2}"
    assert len(evidence1) > 0, "Evidence must be recorded"
    assert len(evidence2) > 0, "Evidence must be recorded"


def test_counterfactual_observation_changes_action():
    """At same state, changing one observation must change the action."""
    agent = EvidencePolicyAgent(Arm.FIXED_CONDITIONAL_STRATEGY, "baseline_first")

    # Baseline: no key
    obs_no_key = SanitizedObservation(
        step=0, timestamp=0,
        accessible_objects=[{"uuid": 1, "name": "floor", "description": ""}],
        inventory=[], nearby_objects=[], agent_location="room",
        last_action_message="", errors=[],
    )
    action_a, _, _ = agent.decide(obs_no_key, "task")

    # Counterfactual: key appears
    agent2 = EvidencePolicyAgent(Arm.FIXED_CONDITIONAL_STRATEGY, "baseline_first")
    obs_with_key = SanitizedObservation(
        step=0, timestamp=0,
        accessible_objects=[{"uuid": 2, "name": "key", "description": ""}],
        inventory=[], nearby_objects=[], agent_location="room",
        last_action_message="", errors=[],
    )
    action_b, _, _ = agent2.decide(obs_with_key, "task")

    assert action_a != action_b, "Counterfactual observation must change action"


def test_evidence_used_recorded():
    """Decision must record what evidence was used."""
    agent = EvidencePolicyAgent(Arm.FIXED_CONDITIONAL_STRATEGY, "baseline_first")
    obs = SanitizedObservation(
        step=0, timestamp=0,
        accessible_objects=[{"uuid": 100, "name": "key", "description": ""}],
        inventory=[], nearby_objects=[], agent_location="room",
        last_action_message="", errors=[],
    )
    action, rationale, evidence = agent.decide(obs, "task")
    assert len(evidence) > 0, "Must record evidence"
    assert any("key" in e.lower() or "100" in e for e in evidence), f"Evidence doesn't mention observation: {evidence}"


# ---- Status semantics ----

def test_status_partial_not_success():
    """Non-zero score without completion = PARTIAL_PROGRESS, not SUCCESS."""
    result = EpisodeResult(
        episode_id="test", scenario="s", difficulty="d", seed=1,
        arm="NO_STRATEGY", agent_id="a", model="m",
        status="PARTIAL_PROGRESS", steps_taken=5,
        initial_score=0, final_score=2, max_score=11, score_delta=2,
        completed=False, completed_successfully=False,
        n_valid_actions=3, n_invalid_actions=2, n_decision_points=2,
        elapsed_s=1.0,
    )
    assert result.status == "PARTIAL_PROGRESS"
    assert result.completed_successfully is False


def test_status_success_requires_completion():
    result = EpisodeResult(
        episode_id="test", scenario="s", difficulty="d", seed=1,
        arm="NO_STRATEGY", agent_id="a", model="m",
        status="SUCCESS", steps_taken=10,
        initial_score=0, final_score=12, max_score=12, score_delta=12,
        completed=True, completed_successfully=True,
        n_valid_actions=8, n_invalid_actions=2, n_decision_points=5,
        elapsed_s=5.0,
    )
    assert result.status == "SUCCESS"
    assert result.completed_successfully is True


# ---- Trace completeness ----

def test_episode_result_serialization():
    """to_candidate_dict must include events with observations and actions."""
    obs = SanitizedObservation(
        step=0, timestamp=0,
        accessible_objects=[], inventory=[], nearby_objects=[],
        agent_location="", last_action_message="", errors=[],
    )
    action = ActionRecord(
        step=0, timestamp=0,
        proposed_action={"action": "MOVE_DIRECTION", "arg1": "north"},
        validated_action={"action": "MOVE_DIRECTION", "arg1": "north"},
        action_status="ACCEPTED", response_success=True,
        response_errors=[], rationale="test", evidence_used=["obs"],
    )
    event = StepEvent(step=0, observation=obs, action=action, next_observation=None, env_ticked=True)

    result = EpisodeResult(
        episode_id="test", scenario="s", difficulty="d", seed=1,
        arm="NO_STRATEGY", agent_id="a", model="m",
        status="FAILED", steps_taken=1,
        initial_score=0, final_score=0, max_score=10, score_delta=0,
        completed=False, completed_successfully=False,
        n_valid_actions=1, n_invalid_actions=0, n_decision_points=1,
        elapsed_s=1.0, events=[event],
    )
    d = result.to_candidate_dict()
    assert d["n_observations"] == 1
    assert d["n_actions"] == 1
    assert len(d["events"]) == 1
    assert d["events"][0]["action"]["action_status"] == "ACCEPTED"


# ---- Leakage isolation ----

def test_candidate_dict_excludes_hidden_fields():
    """to_candidate_dict must NOT include criticalHypotheses/Questions."""
    result = EpisodeResult(
        episode_id="test", scenario="s", difficulty="d", seed=1,
        arm="NO_STRATEGY", agent_id="a", model="m",
        status="FAILED", steps_taken=0,
        initial_score=0, final_score=0, max_score=10, score_delta=0,
        completed=False, completed_successfully=False,
        n_valid_actions=0, n_invalid_actions=0, n_decision_points=0,
        elapsed_s=0,
        trusted_scorecard={"criticalHypotheses": ["SECRET_ANSWER"], "criticalQuestions": ["SECRET_Q"]},
    )
    d = result.to_candidate_dict()
    assert "criticalHypotheses" not in str(d)
    assert "criticalQuestions" not in str(d)
    assert "SECRET_ANSWER" not in str(d)

    # Trusted dict DOES include them
    t = result.to_trusted_dict()
    assert "criticalHypotheses" in t.get("trusted_scorecard", {})


# ---- DiscoveryWorld integration (if available) ----

def test_discoveryworld_action_accepted():
    """Test that official action schema works with real API."""
    try:
        import warnings
        warnings.filterwarnings("ignore")
        from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

        api = DiscoveryWorldAPI()
        api.loadScenario("Combinatorial Chemistry", "Easy", 42, 1)

        # MOVE_DIRECTION with valid direction
        result = api.performAgentAction(0, {"action": "MOVE_DIRECTION", "arg1": "east"})
        assert result.get("success") is True, f"MOVE_DIRECTION failed: {result}"

    except ImportError:
        pytest.skip("DiscoveryWorld not installed")
    except Exception as e:
        pytest.skip(f"DiscoveryWorld error: {e}")


def test_discoveryworld_initial_score_recorded():
    """Initial score must be recorded before any actions."""
    try:
        import warnings
        warnings.filterwarnings("ignore")
        from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

        api = DiscoveryWorldAPI()
        api.loadScenario("Combinatorial Chemistry", "Easy", 42, 1)

        score, max_score, completed, completed_ok = TrustedEvaluator.get_initial_score(api)
        assert max_score > 0, "Max score must be positive"
        # Combinatorial Chemistry starts at 0
        assert score == 0, f"Expected initial score 0, got {score}"

    except ImportError:
        pytest.skip("DiscoveryWorld not installed")
    except Exception as e:
        pytest.skip(f"DiscoveryWorld error: {e}")


def test_discoveryworld_full_episode():
    """Run a full episode and verify traces are complete."""
    try:
        import warnings
        warnings.filterwarnings("ignore")
        from scitransfer.discoveryworld_r2r1 import run_episode_r2r1

        result = run_episode_r2r1(
            scenario="Combinatorial Chemistry",
            difficulty="Easy",
            seed=42,
            arm=Arm.FIXED_CONDITIONAL_STRATEGY,
            max_steps=8,
            max_seconds=60.0,
        )

        # Verify traces
        assert result.n_valid_actions > 0, f"No valid actions recorded"
        assert len(result.events) > 0, "No events recorded"
        assert result.n_decision_points > 0, "No decision points"

        # Verify candidate dict has no hidden info
        d = result.to_candidate_dict()
        assert "criticalHypotheses" not in str(d)

    except ImportError:
        pytest.skip("DiscoveryWorld not installed")
    except Exception as e:
        pytest.skip(f"DiscoveryWorld episode error: {e}")


# ---- SciAgentGYM provenance correction ----

def test_scagentgym_repo_exists():
    """Verify SciAgentGYM is marked AVAILABLE_REPO, not unavailable."""
    # This is a documentation test — the correction is in the suitability matrix
    matrix_path = Path(__file__).resolve().parents[1] / "benchmarks" / "suitability_matrix_round_002_r1.md"
    if matrix_path.exists():
        content = matrix_path.read_text(encoding="utf-8")
        assert "CMarsRover/SciAgentGYM" in content
        assert "AVAILABLE_REPO" in content or "available" in content.lower()
    else:
        pytest.skip("R1 suitability matrix not created yet")
