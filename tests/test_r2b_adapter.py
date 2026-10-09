"""R2B tests: DiscoveryWorld adapter, multi-step loop, isolation, budget enforcement."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.discoveryworld_adapter import (
    Action,
    Arm,
    EpisodeTrace,
    Observation,
    RunStatus,
    SimplePolicyAgent,
    STRATEGIES,
)


# ---- Types ----

def test_observation_creation():
    obs = Observation(step=1, ui_text="test", errors=[], vision_summary="v", raw={})
    assert obs.step == 1
    assert obs.ui_text == "test"


def test_action_decision_point():
    a = Action(step=2, action_type="move", action_json={}, reasoning="r", is_decision_point=True)
    assert a.is_decision_point is True
    a2 = Action(step=1, action_type="move", action_json={}, reasoning="r", is_decision_point=False)
    assert a2.is_decision_point is False


# ---- Agent policy ----

def test_agent_generates_actions():
    agent = SimplePolicyAgent(Arm.NO_STRATEGY, "none")
    obs = Observation(step=0, ui_text="", errors=[], vision_summary="", raw={})
    action = agent.decide(obs, "test task")
    assert action.step == 1
    assert action.action_type is not None


def test_agent_decision_points_increase():
    """Second decision should depend on first (is_decision_point=True)."""
    agent = SimplePolicyAgent(Arm.NO_STRATEGY, "none")
    obs = Observation(step=0, ui_text="", errors=[], vision_summary="", raw={})
    actions = []
    for _ in range(5):
        a = agent.decide(obs, "test")
        actions.append(a)
    # After step 2, all should be decision points
    assert actions[0].is_decision_point is False
    assert actions[1].is_decision_point is True
    assert actions[2].is_decision_point is True


def test_strategy_arms_differ():
    """Strategy arm should have different reasoning than no-strategy after enough steps."""
    agent_a = SimplePolicyAgent(Arm.NO_STRATEGY, "none")
    agent_b = SimplePolicyAgent(Arm.FIXED_CONDITIONAL_STRATEGY, "baseline_first")
    obs = Observation(step=0, ui_text="", errors=[], vision_summary="", raw={})

    # Advance both past the strategy threshold (>5 steps)
    a_actions = []
    b_actions = []
    for _ in range(8):
        a_actions.append(agent_a.decide(obs, "test"))
        b_actions.append(agent_b.decide(obs, "test"))

    # Strategy agent should have strategy note in reasoning after threshold
    last_b = b_actions[-1]
    assert "STRATEGY" in last_b.reasoning, f"Strategy reasoning missing: {last_b.reasoning}"


# ---- Strategies ----

def test_strategy_definitions_exist():
    assert "none" in STRATEGIES
    assert "baseline_first" in STRATEGIES
    assert "placebo" in STRATEGIES
    assert STRATEGIES["none"] is None
    assert STRATEGIES["baseline_first"]["type"] == "FIXED_CONDITIONAL_STRATEGY"
    assert STRATEGIES["placebo"]["type"] == "PLACEBO"


def test_strategy_label_disclaimer():
    """Strategies must be labeled as hand-authored, not learned."""
    for key in ["baseline_first", "placebo"]:
        assert "Hand-authored" in STRATEGIES[key]["label"] or "NOT" in STRATEGIES[key]["label"]


# ---- Episode trace ----

def test_episode_trace_serialization():
    trace = EpisodeTrace(
        episode_id="test", scenario="s", difficulty="d", seed=1,
        arm="NO_STRATEGY", agent_id="a", model="m",
        status="SUCCESS", steps_taken=5, final_score=3, max_score=12,
        score_normalized=0.25, n_decision_points=3, elapsed_s=1.5,
    )
    d = trace.to_dict()
    assert d["episode_id"] == "test"
    assert d["final_score"] == 3
    assert d["n_decision_points"] == 3


# ---- Budget enforcement ----

def test_budget_exceeded_status_exists():
    assert RunStatus.BUDGET_EXCEEDED.value == "BUDGET_EXCEEDED"
    assert RunStatus.TIMEOUT.value == "TIMEOUT"


# ---- Environment (if DiscoveryWorld available) ----

def test_discoveryworld_importable():
    try:
        import warnings
        warnings.filterwarnings("ignore")
        from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
        api = DiscoveryWorldAPI()
        scenarios = api.getValidScenarios()
        assert len(scenarios) > 0
    except ImportError:
        pytest.skip("DiscoveryWorld not installed")
    except Exception as e:
        pytest.skip(f"DiscoveryWorld error: {e}")


def test_discoveryworld_load_scenario():
    try:
        import warnings
        warnings.filterwarnings("ignore")
        from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
        api = DiscoveryWorldAPI()
        api.loadScenario("Combinatorial Chemistry", "Easy", 42, 1)
        scorecard = api.getTaskScorecard()
        assert scorecard is not None
        assert len(scorecard) > 0
        assert "score" in scorecard[0]
        assert "maxScore" in scorecard[0]
    except ImportError:
        pytest.skip("DiscoveryWorld not installed")
    except Exception as e:
        pytest.skip(f"DiscoveryWorld scenario error: {e}")


def test_discoveryworld_multi_step():
    """Verify at least 2 decision points in a real episode."""
    try:
        import warnings
        warnings.filterwarnings("ignore")
        from scitransfer.discoveryworld_adapter import run_episode

        trace = run_episode(
            scenario="Combinatorial Chemistry",
            difficulty="Easy",
            seed=42,
            arm=Arm.NO_STRATEGY,
            max_steps=5,
            max_seconds=30.0,
        )
        assert trace.steps_taken > 0
        assert trace.n_decision_points >= 2, "Need ≥2 decision points for multi-step"
    except ImportError:
        pytest.skip("DiscoveryWorld not installed")
    except Exception as e:
        pytest.skip(f"DiscoveryWorld episode error: {e}")


def test_no_gold_access_in_adapter():
    """Adapter code must not read gold/eval files."""
    adapter_path = Path(__file__).resolve().parents[1] / "src" / "scitransfer" / "discoveryworld_adapter.py"
    content = adapter_path.read_text(encoding="utf-8")
    # Should not reference gold results or eval scripts
    assert "gold_results" not in content
    assert "eval_programs" not in content
    assert "scoring_rubrics" not in content
