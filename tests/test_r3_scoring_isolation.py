"""R3 integration tests: scorer parity, isolation, hash gate, no stale output."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.r3_eval import (
    PROV_DIRECT,
    SCORER_HASHES,
    evaluate_one,
    find_output,
    load_frozen_hashes,
    load_official_scorer,
    prepare_isolated_workdir,
    run_program_isolated,
    score_with_original,
    sha256_file,
    verify_program_hash,
    R3_RUNS,
)


# ---------------------------------------------------------------------------
# Scorer parity (R3-03)
# ---------------------------------------------------------------------------

def test_scorer_hashes_match_frozen():
    for tid, expected in SCORER_HASHES.items():
        mod, actual = load_official_scorer(tid)
        assert actual == expected, f"Task {tid} scorer hash mismatch"


def test_scorer_85_accepts_exact_match(tmp_path):
    """Perfect output should score 1."""
    mod, _ = load_official_scorer(85)
    # Create minimal fixture
    gold = {"sub1": {"value": 1.0, "label": "a"}}
    pred = {"sub1": {"value": 1.0, "label": "a"}}
    gold_dir = tmp_path / "benchmark" / "eval_programs" / "gold_results"
    pred_dir = tmp_path / "pred_results"
    gold_dir.mkdir(parents=True)
    pred_dir.mkdir(parents=True)
    (gold_dir / "biopsykit_saliva_gold.json").write_text(json.dumps(gold))
    (pred_dir / "saliva_pred.json").write_text(json.dumps(pred))

    old_cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        score, log = mod.eval()
        assert score == 1
    finally:
        os.chdir(old_cwd)


def test_scorer_85_rejects_wrong_value(tmp_path):
    mod, _ = load_official_scorer(85)
    gold = {"sub1": {"value": 1.0, "label": "a"}}
    pred = {"sub1": {"value": 999.0, "label": "a"}}
    gold_dir = tmp_path / "benchmark" / "eval_programs" / "gold_results"
    pred_dir = tmp_path / "pred_results"
    gold_dir.mkdir(parents=True)
    pred_dir.mkdir(parents=True)
    (gold_dir / "biopsykit_saliva_gold.json").write_text(json.dumps(gold))
    (pred_dir / "saliva_pred.json").write_text(json.dumps(pred))

    old_cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        score, log = mod.eval()
        assert score == 0
    finally:
        os.chdir(old_cwd)


def test_scorer_16_allows_extra_rows(tmp_path):
    """Official #16 allows extra rows (set coverage). This is NOT exact match."""
    mod, _ = load_official_scorer(16)
    gold_lines = ["line_A", "line_B", "line_C"]
    pred_lines = ["line_A", "line_B", "line_C", "extra_row"]  # extra allowed
    gold_dir = tmp_path / "benchmark" / "eval_programs" / "gold_results"
    pred_dir = tmp_path / "pred_results"
    gold_dir.mkdir(parents=True)
    pred_dir.mkdir(parents=True)
    (gold_dir / "antibioticsai_filter_gold_results.txt").write_text("\n".join(gold_lines))
    (pred_dir / "compound_filter_results.txt").write_text("\n".join(pred_lines))

    old_cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        score, log = mod.eval()
        assert score == 1, f"Extra rows should be allowed (set coverage), got {score}"
    finally:
        os.chdir(old_cwd)


def test_scorer_16_rejects_missing_gold_lines(tmp_path):
    mod, _ = load_official_scorer(16)
    gold_lines = ["line_A", "line_B", "line_C"]
    pred_lines = ["line_A", "line_B"]  # missing line_C
    gold_dir = tmp_path / "benchmark" / "eval_programs" / "gold_results"
    pred_dir = tmp_path / "pred_results"
    gold_dir.mkdir(parents=True)
    pred_dir.mkdir(parents=True)
    (gold_dir / "antibioticsai_filter_gold_results.txt").write_text("\n".join(gold_lines))
    (pred_dir / "compound_filter_results.txt").write_text("\n".join(pred_lines))

    old_cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        score, log = mod.eval()
        assert score == 0
    finally:
        os.chdir(old_cwd)


def test_scorer_21_accepts_within_tolerance(tmp_path):
    """Official #21 uses 5% relative error tolerance, NOT exact match."""
    mod, _ = load_official_scorer(21)
    gold_val = 100.0
    pred_val = 103.0  # 3% off, within 5%
    gold_dir = tmp_path / "benchmark" / "eval_programs" / "gold_results"
    pred_dir = tmp_path / "pred_results"
    gold_dir.mkdir(parents=True)
    pred_dir.mkdir(parents=True)
    (gold_dir / "deforestation_rate_gold.csv").write_text(
        f"percentage_deforestation\n{gold_val}\n"
    )
    (pred_dir / "deforestation_rate.csv").write_text(
        f"percentage_deforestation\n{pred_val}\n"
    )

    old_cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        score, log = mod.eval()
        assert score == 1, f"3% deviation should pass 5% threshold, got {score}"
    finally:
        os.chdir(old_cwd)


def test_scorer_21_rejects_outside_tolerance(tmp_path):
    mod, _ = load_official_scorer(21)
    gold_val = 100.0
    pred_val = 200.0  # 100% off
    gold_dir = tmp_path / "benchmark" / "eval_programs" / "gold_results"
    pred_dir = tmp_path / "pred_results"
    gold_dir.mkdir(parents=True)
    pred_dir.mkdir(parents=True)
    (gold_dir / "deforestation_rate_gold.csv").write_text(
        f"percentage_deforestation\n{gold_val}\n"
    )
    (pred_dir / "deforestation_rate.csv").write_text(
        f"percentage_deforestation\n{pred_val}\n"
    )

    old_cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        score, log = mod.eval()
        assert score == 0
    finally:
        os.chdir(old_cwd)


# ---------------------------------------------------------------------------
# Hash gate (R3-02)
# ---------------------------------------------------------------------------

def test_hash_mismatch_blocks_execution(tmp_path):
    """Full SHA mismatch must be rejected before running."""
    # Create a fake program
    fake_prog = tmp_path / "pred_fake.py"
    fake_prog.write_text("print('fake')")

    expected_sha = "0000000000000000000000000000000000000000000000000000000000000000"
    assert verify_program_hash(fake_prog, expected_sha) is False


def test_hash_match_passes_gate(tmp_path):
    prog = tmp_path / "pred_ok.py"
    prog.write_text("print('ok')")
    actual = sha256_file(prog)
    assert verify_program_hash(prog, actual) is True


# ---------------------------------------------------------------------------
# Isolation (R3-02, R3-03)
# ---------------------------------------------------------------------------

def test_isolated_workdir_no_reuse(tmp_path, monkeypatch):
    """Refusing to reuse an existing run directory."""
    monkeypatch.setattr("scitransfer.r3_eval.R3_RUNS", tmp_path)

    # First call should work
    prog = tmp_path / "test_prog.py"
    prog.write_text("print('test')")

    # We need a valid task_id for the test
    # Use 85 as it has the simplest gold structure
    workdir, staged = prepare_isolated_workdir(85, "NO_STRATEGY", 999, prog)
    assert workdir.exists()
    assert staged.exists()
    assert (workdir / "pred_results").is_dir()

    # Second call with same params should fail
    with pytest.raises(FileExistsError):
        prepare_isolated_workdir(85, "NO_STRATEGY", 999, prog)


def test_no_shared_pred_results_between_arms(tmp_path, monkeypatch):
    """A and B must use different workdirs and pred_results."""
    monkeypatch.setattr("scitransfer.r3_eval.R3_RUNS", tmp_path)

    prog = tmp_path / "test_prog.py"
    prog.write_text("print('test')")

    workdir_a, _ = prepare_isolated_workdir(85, "NO_STRATEGY", 998, prog)
    workdir_b, _ = prepare_isolated_workdir(85, "FIXED_STRATEGY", 998, prog)

    assert workdir_a != workdir_b
    assert (workdir_a / "pred_results") != (workdir_b / "pred_results")


# ---------------------------------------------------------------------------
# No stale output (R3-04)
# ---------------------------------------------------------------------------

def test_no_output_returns_none(tmp_path):
    """find_output returns None when no output exists."""
    workdir = tmp_path
    (workdir / "pred_results").mkdir()
    assert find_output(workdir, 85) is None
    assert find_output(workdir, 16) is None
    assert find_output(workdir, 21) is None


# ---------------------------------------------------------------------------
# Scorer exception propagates (official harness catches and returns 0)
# ---------------------------------------------------------------------------

def test_scorer_exception_propagates(tmp_path):
    """If scorer throws (e.g. FileNotFoundError), exception propagates.
    Official harness (compute_scores.py) catches this and returns 0."""
    workdir = tmp_path / "workdir"
    (workdir / "pred_results").mkdir(parents=True)
    # No benchmark/ junction → scorer can't find gold → FileNotFoundError

    with pytest.raises(Exception):
        score_with_original(85, workdir)


# ---------------------------------------------------------------------------
# Full hash catalog integrity
# ---------------------------------------------------------------------------

def test_frozen_hash_catalog_has_all_runs():
    hashes = load_frozen_hashes()
    expected_runs = [
        "sab_verified_85__NO_STRATEGY__seed0",
        "sab_verified_85__FIXED_STRATEGY__seed0",
        "sab_verified_16__NO_STRATEGY__seed0",
        "sab_verified_16__FIXED_STRATEGY__seed0",
        "sab_verified_21__NO_STRATEGY__seed0",
        "sab_verified_21__FIXED_STRATEGY__seed0",
    ]
    for run in expected_runs:
        assert run in hashes, f"Missing {run} in hash catalog"
        assert len(hashes[run]) == 64, f"Hash for {run} is not 64 hex chars"
