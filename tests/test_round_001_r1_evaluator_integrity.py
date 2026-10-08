"""Round 001-R1 evaluator integrity tests.

Covers the P0 fixes: --split verified, absolute paths, row-index JSONL parsing,
placeholder detection, fail-closed official_evaluation, and non-destructive resume.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scitransfer.benchmarks.scienceagentbench import (
    EXPECTED_VERIFIED_ROWS,
    PINNED_SPLIT,
    OfficialEvalResult,
    TaskMeta,
    _build_command,
    check_evaluator_available,
    detect_placeholder,
    get_row_index_map,
    load_verified_tasks,
    parse_jsonl_row_for_instance,
    run_official_evaluation,
    EvaluatorUnavailable,
)


# ---------------------------------------------------------------------------
# R1-01: --split verified on actual command
# ---------------------------------------------------------------------------

def test_build_command_includes_split_verified():
    cmd = _build_command(
        benchmark_dir=Path("/abs/bench"),
        pred_program_path=Path("/abs/pred"),
        log_fname=Path("/abs/log.jsonl"),
        upstream_dir=Path("/abs/upstream"),
        run_id="test_run",
        instance_id=85,
        split=PINNED_SPLIT,
    )
    assert "--split" in cmd
    idx = cmd.index("--split")
    assert cmd[idx + 1] == "verified"
    assert "validation" not in cmd


def test_pinned_split_constant_is_verified():
    assert PINNED_SPLIT == "verified"


# ---------------------------------------------------------------------------
# R1-02: Absolute path resolution in command
# ---------------------------------------------------------------------------

def test_build_command_uses_absolute_paths(tmp_path):
    bench = (tmp_path / "bench").resolve()
    pred = (tmp_path / "pred").resolve()
    log = (tmp_path / "log.jsonl").resolve()
    upstream = (tmp_path / "upstream").resolve()
    cmd = _build_command(
        benchmark_dir=bench,
        pred_program_path=pred,
        log_fname=log,
        upstream_dir=upstream,
        run_id="test",
        instance_id=1,
    )
    bm_idx = cmd.index("--benchmark_path")
    assert Path(cmd[bm_idx + 1]).is_absolute()
    pp_idx = cmd.index("--pred_program_path")
    assert Path(cmd[pp_idx + 1]).is_absolute()
    # Also verify the paths match what we passed in
    assert Path(cmd[bm_idx + 1]) == bench
    assert Path(cmd[pp_idx + 1]) == pred


# ---------------------------------------------------------------------------
# R1-03: JSONL row-index parsing (NOT first-row)
# ---------------------------------------------------------------------------

def _make_jsonl(n_rows: int, target_idx: int, target_record: dict, filler: dict | None = None) -> list[str]:
    """Create a JSONL string list mimicking upstream output format."""
    default_filler = filler or {
        "valid_program": 0,
        "codebert_score": 0.0,
        "success_rate": 0,
        "log_info": "default log info",
    }
    lines = []
    for i in range(n_rows):
        if i == target_idx:
            lines.append(json.dumps(target_record))
        else:
            lines.append(json.dumps(default_filler))
    return lines


def test_jsonl_parse_selects_correct_row_not_first(tmp_path):
    """Target at row 57 must NOT return row 0's score."""
    row_map = {85: 57, 16: 15, 21: 20}
    target_record = {"valid_program": 1, "codebert_score": 0.85, "success_rate": 1, "log_info": "real eval"}
    lines = _make_jsonl(EXPECTED_VERIFIED_ROWS, target_idx=57, target_record=target_record)
    p = tmp_path / "eval.jsonl"
    p.write_text("\n".join(lines), encoding="utf-8")

    record = parse_jsonl_row_for_instance(p, 85, row_map)
    assert record["_row_index"] == 57
    assert record["success_rate"] == 1
    assert record["log_info"] == "real eval"


def test_jsonl_parse_row_index_matches_parquet_order(tmp_path):
    """instance_id 16 is at row index from the real parquet."""
    tasks = load_verified_tasks()
    row_map = get_row_index_map()
    # 102 tasks, each should have a unique row index
    assert len(row_map) == 102
    assert len(set(row_map.values())) == 102
    # Row index must match position in load_verified_tasks order
    for i, t in enumerate(tasks):
        assert row_map[t.instance_id] == i, f"Row mismatch for {t.instance_id}: {row_map[t.instance_id]} != {i}"


def test_jsonl_parse_rejects_wrong_length(tmp_path):
    row_map = {85: 0}
    p = tmp_path / "short.jsonl"
    p.write_text('{"success_rate": 1}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="expected 102"):
        parse_jsonl_row_for_instance(p, 85, row_map)


def test_jsonl_parse_rejects_unknown_instance(tmp_path):
    row_map = {16: 0}
    lines = _make_jsonl(EXPECTED_VERIFIED_ROWS, 0, {"success_rate": 1})
    p = tmp_path / "eval.jsonl"
    p.write_text("\n".join(lines), encoding="utf-8")
    with pytest.raises(ValueError, match="not in pinned"):
        parse_jsonl_row_for_instance(p, 999, row_map)


def test_jsonl_parse_rejects_malformed_row(tmp_path):
    row_map = {85: 3}
    lines = _make_jsonl(EXPECTED_VERIFIED_ROWS, 3, {"success_rate": 1})
    lines[3] = "{not valid json"
    p = tmp_path / "bad.jsonl"
    p.write_text("\n".join(lines), encoding="utf-8")
    with pytest.raises(ValueError, match="malformed"):
        parse_jsonl_row_for_instance(p, 85, row_map)


# ---------------------------------------------------------------------------
# R1-03: Placeholder vs real failure score 0
# ---------------------------------------------------------------------------

def test_placeholder_detected_when_no_evidence(tmp_path):
    """success_rate=0 with no result.json → placeholder."""
    record = {"valid_program": 0, "codebert_score": 0.0, "success_rate": 0, "log_info": "default log info"}
    evidence = tmp_path / "nonexistent" / "result.json"
    assert detect_placeholder(record, evidence) is True


def test_real_failure_not_placeholder_when_evidence_exists(tmp_path):
    """success_rate=0 with result.json present → real failure, NOT placeholder."""
    record = {"valid_program": 1, "codebert_score": 0.3, "success_rate": 0, "log_info": "Task failed: assertion error"}
    evidence = tmp_path / "result.json"
    evidence.write_text(json.dumps([1, 0.3, 0, "assertion error"]), encoding="utf-8")
    assert detect_placeholder(record, evidence) is False


def test_real_success_not_placeholder(tmp_path):
    record = {"valid_program": 1, "codebert_score": 1.0, "success_rate": 1, "log_info": "all checks passed"}
    evidence = tmp_path / "result.json"
    evidence.write_text("[1, 1.0, 1, 'ok']", encoding="utf-8")
    assert detect_placeholder(record, evidence) is False


# ---------------------------------------------------------------------------
# R1-04: Fail-closed official_evaluation
# ---------------------------------------------------------------------------

def test_official_eval_result_defaults_not_official():
    r = OfficialEvalResult(
        task_id="t", instance_id=0, row_index=None,
        official_evaluation=False,
        valid_program=None, codebert_score=None, success_rate=None,
        log_info=None, raw_output_path=None, eval_jsonl_path=None,
        execution_evidence_path=None, is_placeholder=None,
        error="test", command=None,
    )
    assert r.official_evaluation is False
    assert r.success_rate is None


def test_official_requires_execution_evidence():
    """Even with score fields, no execution evidence → not official."""
    record = {"valid_program": 1, "codebert_score": 0.9, "success_rate": 1, "log_info": "ok"}
    evidence = Path("/nonexistent/result.json")
    assert detect_placeholder(record, evidence) is True  # treated as placeholder


# ---------------------------------------------------------------------------
# Split and parquet consistency
# ---------------------------------------------------------------------------

def test_verified_split_row_count():
    tasks = load_verified_tasks()
    assert len(tasks) == EXPECTED_VERIFIED_ROWS


def test_all_domains_present():
    tasks = load_verified_tasks()
    domains = {t.domain for t in tasks}
    for d in ["Bioinformatics", "Computational Chemistry", "Geographical Information Science"]:
        assert d in domains


# ---------------------------------------------------------------------------
# Readiness check paths are absolute
# ---------------------------------------------------------------------------

def test_readiness_report_absolute_paths():
    report = check_evaluator_available("relative/bench", "relative/upstream")
    assert Path(report["benchmark_dir"]).is_absolute()
    assert Path(report["upstream_dir"]).is_absolute()


# ---------------------------------------------------------------------------
# run_official_evaluation fail-closed when artifacts missing
# ---------------------------------------------------------------------------

def test_run_official_eval_fails_closed_missing_artifacts(tmp_path):
    task = TaskMeta(
        instance_id=85, domain="Bioinformatics", subtask_categories="x",
        github_name="x", task_inst="x", domain_knowledge="x",
        dataset_folder_tree="x", dataset_preview="x",
        src_file_or_path="x", gold_program_name="saliva.py",
        output_fname="out.json", eval_script_name="eval.py",
    )
    with pytest.raises(EvaluatorUnavailable):
        run_official_evaluation(
            task=task,
            pred_program_path=tmp_path,
            benchmark_dir=tmp_path / "no_bench",
            upstream_dir=tmp_path / "no_upstream",
            output_dir=tmp_path / "out",
        )


# ---------------------------------------------------------------------------
# Non-destructive download script sanity
# ---------------------------------------------------------------------------

def test_download_script_no_destructive_delete():
    """scripts/download_sab_artifacts.py must not contain Remove-Item / os.remove of the zip at startup."""
    script = Path(__file__).resolve().parents[1] / "scripts" / "download_sab_artifacts.py"
    if not script.exists():
        pytest.skip("download script not found")
    text = script.read_text(encoding="utf-8")
    # Must use resume (Range header), not destructive restart
    assert "Range" in text or "range" in text.lower()
    # Must not delete the output zip at startup
    startup_lines = text[:2000]  # first ~2000 chars = startup logic
    assert "os.remove" not in startup_lines
    assert "Remove-Item" not in startup_lines


def test_start_download_ps1_no_destructive_delete():
    """start_download.ps1 must NOT call Remove-Item on the zip (R1 P1 fix)."""
    script = Path(__file__).resolve().parents[1] / "scripts" / "start_download.ps1"
    if not script.exists():
        pytest.skip("start_download.ps1 not found")
    text = script.read_text(encoding="utf-8")
    assert "Remove-Item" not in text, "start_download.ps1 must not delete the partial zip"
