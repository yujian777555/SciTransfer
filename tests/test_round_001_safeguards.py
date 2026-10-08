"""Mandatory verification tests for SciTransfer Round 001.

Covers: initial-state parity, prompt/strategy hash provenance, budget handling,
missing-evaluator fail-closed, no answer-key leakage, synthetic-not-official,
trace schema, run-folder isolation, explicit failure statuses, official score parsing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.agent import (  # noqa: E402
    FIXED_STRATEGY,
    build_prompt,
    extract_python_program,
    sha256_of,
)
from scitransfer.benchmarks.scienceagentbench import (  # noqa: E402
    EvaluatorUnavailable,
    check_evaluator_available,
    get_task,
    load_verified_tasks,
    run_official_evaluation,
    TaskMeta,
)
from scitransfer.core.types import Arm, Budget, RunResult, ScientificStrategy, stable_json  # noqa: E402
from scitransfer.metrics import paired_difference, parse_official_score  # noqa: E402
from scitransfer.runner.paired import environment_fingerprint, run_single_arm  # noqa: E402
from scitransfer.runner.trace import TraceLogger, sanitize_secrets  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Task / split isolation
# ---------------------------------------------------------------------------

def test_verified_split_loads_102_tasks():
    tasks = load_verified_tasks()
    assert len(tasks) == 102


def test_verified_split_has_required_domains():
    tasks = load_verified_tasks()
    domains = {t.domain for t in tasks}
    assert "Bioinformatics" in domains
    assert "Computational Chemistry" in domains
    assert "Geographical Information Science" in domains


def test_task_ids_unique_and_stable():
    tasks = load_verified_tasks()
    ids = [t.instance_id for t in tasks]
    assert len(ids) == len(set(ids))
    t = get_task(ids[0])
    assert t.task_key == f"sab_verified_{ids[0]}"


def test_no_answer_key_fields_in_task_metadata():
    """Task metadata must not contain gold program source or eval answers."""
    tasks = load_verified_tasks()
    for t in tasks:
        d = t.to_dict()
        # gold_program_name is a filename, not the source. The source itself
        # lives only in the password-protected benchmark zip, not in the HF split.
        assert "gold_program_source" not in d
        assert "eval_answer" not in d
        assert "canary GUID" not in t.task_inst


# ---------------------------------------------------------------------------
# 2. Prompt / strategy hash and provenance
# ---------------------------------------------------------------------------

def _sample_task_dict() -> dict:
    return {
        "task_inst": "Write a program that computes X.",
        "dataset_folder_tree": "datasets/\n  x.csv",
        "dataset_preview": "x\n1\n2",
    }


def test_arm_a_and_b_prompts_differ_and_hashes_recorded():
    prompt_a, sid_a, sh_a = build_prompt(_sample_task_dict(), Arm.NO_STRATEGY)
    prompt_b, sid_b, sh_b = build_prompt(_sample_task_dict(), Arm.FIXED_STRATEGY)
    assert prompt_a != prompt_b
    assert sid_a is None and sh_a is None
    assert sid_b == FIXED_STRATEGY.strategy_id
    assert sh_b is not None and len(sh_b) == 64
    # Strategy block must be present in B and absent in A.
    assert "RESEARCH STRATEGY" in prompt_b
    assert "RESEARCH STRATEGY" not in prompt_a


def test_prompt_hash_is_deterministic():
    p1, _, _ = build_prompt(_sample_task_dict(), Arm.NO_STRATEGY)
    p2, _, _ = build_prompt(_sample_task_dict(), Arm.NO_STRATEGY)
    assert sha256_of(p1) == sha256_of(p2)


def test_strategy_hash_provenance_stable():
    h1 = sha256_of(stable_json(FIXED_STRATEGY.to_dict()))
    h2 = sha256_of(stable_json(FIXED_STRATEGY.to_dict()))
    assert h1 == h2
    assert FIXED_STRATEGY.source_provenance
    assert FIXED_STRATEGY.preconditions
    assert FIXED_STRATEGY.research_action
    assert FIXED_STRATEGY.expected_evidence
    assert FIXED_STRATEGY.invalidity_conditions


def test_placebo_arm_has_neutral_block_not_strategy():
    prompt, sid, sh = build_prompt(_sample_task_dict(), Arm.PLACEBO)
    assert "NEUTRAL CONTEXT" in prompt
    assert "RESEARCH STRATEGY" not in prompt
    assert sid is None


# ---------------------------------------------------------------------------
# 3. Budget handling
# ---------------------------------------------------------------------------

def test_budget_defaults_and_to_dict():
    b = Budget()
    assert b.max_tokens > 0
    assert b.max_cost_usd > 0
    d = b.to_dict()
    assert set(d) == {"max_tokens", "max_cost_usd", "timeout_s"}


# ---------------------------------------------------------------------------
# 4. Missing-evaluator fail-closed
# ---------------------------------------------------------------------------

def test_missing_evaluator_raises_unavailable(tmp_path):
    fake_bench = tmp_path / "no_bench"
    fake_upstream = tmp_path / "no_upstream"
    task = TaskMeta(
        instance_id=0, domain="TestDomain", subtask_categories="x", github_name="x/x",
        task_inst="x", domain_knowledge="x", dataset_folder_tree="x", dataset_preview="x",
        src_file_or_path="x", gold_program_name="x.py", output_fname="out.txt",
        eval_script_name="e.py",
    )
    with pytest.raises(EvaluatorUnavailable) as exc:
        run_official_evaluation(
            task=task,
            pred_program_path=tmp_path,
            benchmark_dir=fake_bench,
            upstream_dir=fake_upstream,
            output_dir=tmp_path / "out",
        )
    assert "not runnable" in str(exc.value).lower() or "Missing" in str(exc.value)


def test_evaluator_readiness_reports_missing_artifacts():
    report = check_evaluator_available("nonexistent_bench", "nonexistent_upstream")
    assert report["ready"] is False
    assert report["benchmark_dir_exists"] is False


# ---------------------------------------------------------------------------
# 5. Synthetic tasks are never counted as official success
# ---------------------------------------------------------------------------

def test_synthetic_score_is_not_official():
    """A fabricated/synthetic evaluation record must not parse as official."""
    synthetic = {
        "official_evaluation": False,
        "success_rate": 1.0,  # even if a score is present
        "valid_program": 1,
        "codebert_score": 0.9,
    }
    assert parse_official_score(synthetic) is None

    synthetic_mock = {
        "official_evaluation": True,
        "success_rate": None,  # no real score
    }
    assert parse_official_score(synthetic_mock) is None

    genuine = {
        "official_evaluation": True,
        "success_rate": 1,
    }
    assert parse_official_score(genuine) == 1.0


def test_run_result_official_flag_gates_score():
    r = RunResult(
        task_id="t", domain="d", arm="A", seed=0, agent_id="a", agent_model="m",
        status="SUCCESS", score=1.0, official_evaluation=False,
        cost_usd=0.0, tokens_in=0, tokens_out=0, prompt_hash="h",
        strategy_id=None, strategy_hash=None, environment_sha="e",
        trace_path=None, evaluator_output_path=None,
        error=None, exit_reason="test", started_at="s", finished_at="f",
    )
    # Score exists but not official — consumers must check the flag.
    assert r.official_evaluation is False
    assert parse_official_score(r.to_dict()) is None


# ---------------------------------------------------------------------------
# 6. Trace schema and run-folder isolation
# ---------------------------------------------------------------------------

def _mock_agent_response(prompt: str, **kwargs):
    """Deterministic offline stand-in for call_deepseek (no network)."""
    from scitransfer.agent import AgentResponse

    program = "print('mock program for isolation test')\n"
    return AgentResponse(
        text=f"```python\n{program}```",
        program=program,
        prompt=prompt,
        prompt_hash=sha256_of(prompt),
        strategy_id=None,
        strategy_hash=None,
        model="mock-model",
        tokens_in=10,
        tokens_out=20,
        cost_usd=0.0,
        error=None,
    )


def _mock_agent_error(prompt: str, **kwargs):
    from scitransfer.agent import AgentResponse

    return AgentResponse(
        text="", program=None, prompt=prompt, prompt_hash=sha256_of(prompt),
        strategy_id=None, strategy_hash=None, model="mock-model",
        tokens_in=0, tokens_out=0, cost_usd=0.0,
        error="Mock agent error for testing.",
    )


def test_trace_logger_appends_jsonl(tmp_path):
    tl = TraceLogger(tmp_path / "trace.jsonl")
    tl.append({"event": "a", "n": 1})
    tl.append({"event": "b", "n": 2})
    rows = tl.read_all()
    assert len(rows) == 2
    assert rows[0]["event"] == "a"
    assert rows[1]["event"] == "b"


def test_trace_refuses_overwrite(tmp_path):
    p = tmp_path / "trace.jsonl"
    TraceLogger(p)
    with pytest.raises(FileExistsError):
        TraceLogger(p)


def test_run_folder_isolation(tmp_path, monkeypatch):
    """Two arms must write into separate directories."""
    monkeypatch.setattr("scitransfer.runner.paired.call_deepseek", _mock_agent_response)

    task = TaskMeta(
        instance_id=99999, domain="TestDomain", subtask_categories="x", github_name="x/x",
        task_inst="x", domain_knowledge="x", dataset_folder_tree="x", dataset_preview="x",
        src_file_or_path="x", gold_program_name="x.py", output_fname="out.txt",
        eval_script_name="e.py",
    )
    ra = run_single_arm(task, Arm.NO_STRATEGY, 0, tmp_path, skip_evaluation=True)
    rb = run_single_arm(task, Arm.FIXED_STRATEGY, 0, tmp_path, skip_evaluation=True)
    dir_a = Path(ra.extra["prompt_path"]).parent
    dir_b = Path(rb.extra["prompt_path"]).parent
    assert dir_a != dir_b
    assert dir_a.exists() and dir_b.exists()
    assert (dir_a / "trace.jsonl").exists()
    assert (dir_b / "trace.jsonl").exists()
    # B must have a strategy file, A must not.
    assert (dir_b / "strategy.json").exists()
    assert not (dir_a / "strategy.json").exists()


# ---------------------------------------------------------------------------
# 7. Explicit failure statuses
# ---------------------------------------------------------------------------

def test_run_without_evaluator_marks_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr("scitransfer.runner.paired.call_deepseek", _mock_agent_response)

    task = TaskMeta(
        instance_id=99998, domain="TestDomain", subtask_categories="x", github_name="x/x",
        task_inst="x", domain_knowledge="x", dataset_folder_tree="x", dataset_preview="x",
        src_file_or_path="x", gold_program_name="x.py", output_fname="out.txt",
        eval_script_name="e.py",
    )
    # Real call with missing evaluator → must be BLOCKED, not SUCCESS.
    result = run_single_arm(task, Arm.NO_STRATEGY, 0, tmp_path, skip_evaluation=False)
    assert result.status == "BLOCKED"
    assert result.official_evaluation is False
    assert result.score is None
    assert result.error is not None
    assert result.exit_reason in (
        "official_evaluator_unavailable",
        "official_evaluator_unavailable_or_failed",
        "agent_error",
    )


def test_skip_evaluation_is_blocked_not_success(tmp_path, monkeypatch):
    monkeypatch.setattr("scitransfer.runner.paired.call_deepseek", _mock_agent_response)

    task = TaskMeta(
        instance_id=99997, domain="TestDomain", subtask_categories="x", github_name="x/x",
        task_inst="x", domain_knowledge="x", dataset_folder_tree="x", dataset_preview="x",
        src_file_or_path="x", gold_program_name="x.py", output_fname="out.txt",
        eval_script_name="e.py",
    )
    result = run_single_arm(task, Arm.NO_STRATEGY, 0, tmp_path, skip_evaluation=True)
    assert result.status == "BLOCKED"
    assert result.score is None
    assert result.official_evaluation is False


def test_agent_error_marks_error_status(tmp_path, monkeypatch):
    monkeypatch.setattr("scitransfer.runner.paired.call_deepseek", _mock_agent_error)

    task = TaskMeta(
        instance_id=99996, domain="TestDomain", subtask_categories="x", github_name="x/x",
        task_inst="x", domain_knowledge="x", dataset_folder_tree="x", dataset_preview="x",
        src_file_or_path="x", gold_program_name="x.py", output_fname="out.txt",
        eval_script_name="e.py",
    )
    result = run_single_arm(task, Arm.NO_STRATEGY, 0, tmp_path, skip_evaluation=True)
    assert result.status == "ERROR"
    assert result.exit_reason == "agent_error"
    assert result.official_evaluation is False


# ---------------------------------------------------------------------------
# 8. Official evaluator output parsing
# ---------------------------------------------------------------------------

def test_paired_difference_with_none():
    assert paired_difference(1.0, 0.0) == 1.0
    assert paired_difference(None, 0.0) is None
    assert paired_difference(1.0, None) is None


def test_parse_official_score_requires_flag():
    assert parse_official_score({"official_evaluation": True, "success_rate": 0}) == 0.0
    assert parse_official_score({"official_evaluation": True, "success_rate": 1}) == 1.0
    assert parse_official_score({"official_evaluation": False, "success_rate": 1}) is None
    assert parse_official_score({}) is None


# ---------------------------------------------------------------------------
# 9. Secret sanitization
# ---------------------------------------------------------------------------

def test_sanitize_secrets_redacts_keys():
    s = "key sk-abc123def456ghi789 and api_key=sk-xyz987654321"
    red = sanitize_secrets(s)
    assert "sk-abc123def456ghi789" not in red
    assert "sk-xyz987654321" not in red
    assert "REDACTED" in red


# ---------------------------------------------------------------------------
# 10. Program extraction
# ---------------------------------------------------------------------------

def test_extract_python_program():
    text = "Here is the code:\n```python\nprint('hi')\n```\ndone"
    assert extract_python_program(text) == "print('hi')"
    assert extract_python_program("no code here") is None


# ---------------------------------------------------------------------------
# 11. Environment fingerprint is stable within a machine
# ---------------------------------------------------------------------------

def test_environment_fingerprint_stable():
    e1 = environment_fingerprint()
    e2 = environment_fingerprint()
    assert e1 == e2
    assert len(e1) == 16
