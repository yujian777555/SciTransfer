"""ScienceAgentBench loader and official evaluator interface.

Fails closed when the verified evaluator or its artifacts are missing.
Never fabricates scores.

R1 fixes:
- Explicitly pass ``--split verified`` (upstream defaults to ``validation``).
- All paths resolved to absolute before subprocess cwd switch.
- JSONL parsing maps instance_id -> row index of the SAME pinned verified split.
- Placeholder / filler rows rejected as genuine evaluation.
- ``official_evaluation=True`` only when execution evidence + correct row match.
"""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from ..core.types import sha256_of, stable_json

# ---- Pinned constants (R1) ----
PINNED_HF_SHA = "9c6e96c9e74572e979b0930ee735041cef528cb7"
PINNED_UPSTREAM_COMMIT = "c26e151ed601ba109dc4d35e057ff8e73fec469d"
PINNED_SPLIT = "verified"  # NOT "validation"

DEFAULT_PARQUET = Path("benchmarks/data/verified-00000-of-00001.parquet")
DEFAULT_BENCHMARK_DIR = Path("benchmarks/ScienceAgentBench/benchmark")
DEFAULT_UPSTREAM_DIR = Path("benchmarks/ScienceAgentBench-upstream")

# Row count of the verified split — used for JSONL length validation.
EXPECTED_VERIFIED_ROWS = 102


@dataclass(frozen=True)
class TaskMeta:
    instance_id: int
    domain: str
    subtask_categories: str
    github_name: str
    task_inst: str
    domain_knowledge: str
    dataset_folder_tree: str
    dataset_preview: str
    src_file_or_path: str
    gold_program_name: str
    output_fname: str
    eval_script_name: str

    @property
    def task_key(self) -> str:
        return f"sab_verified_{self.instance_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "domain": self.domain,
            "subtask_categories": self.subtask_categories,
            "github_name": self.github_name,
            "task_inst": self.task_inst,
            "domain_knowledge": self.domain_knowledge,
            "dataset_folder_tree": self.dataset_folder_tree,
            "dataset_preview": self.dataset_preview,
            "src_file_or_path": self.src_file_or_path,
            "gold_program_name": self.gold_program_name,
            "output_fname": self.output_fname,
            "eval_script_name": self.eval_script_name,
        }


# ---------------------------------------------------------------------------
# Dataset loading — pinned verified split
# ---------------------------------------------------------------------------

def load_verified_tasks(parquet_path: Path | str = DEFAULT_PARQUET) -> list[TaskMeta]:
    """Load the official verified split (102 tasks)."""
    path = Path(parquet_path).resolve()
    if not path.exists():
        raise FileNotFoundError(
            f"Verified ScienceAgentBench parquet not found: {path}. "
            "Download from https://huggingface.co/datasets/osunlp/ScienceAgentBench "
            "(split=verified)."
        )
    df = pd.read_parquet(path)
    tasks: list[TaskMeta] = []
    for _, row in df.iterrows():
        tasks.append(
            TaskMeta(
                instance_id=int(row["instance_id"]),
                domain=str(row["domain"]),
                subtask_categories=str(row["subtask_categories"]),
                github_name=str(row["github_name"]),
                task_inst=str(row["task_inst"]),
                domain_knowledge=str(row["domain_knowledge"]),
                dataset_folder_tree=str(row["dataset_folder_tree"]),
                dataset_preview=str(row["dataset_preview"]),
                src_file_or_path=str(row["src_file_or_path"]),
                gold_program_name=str(row["gold_program_name"]),
                output_fname=str(row["output_fname"]),
                eval_script_name=str(row["eval_script_name"]),
            )
        )
    return tasks


def get_task(instance_id: int, parquet_path: Path | str = DEFAULT_PARQUET) -> TaskMeta:
    for t in load_verified_tasks(parquet_path):
        if t.instance_id == instance_id:
            return t
    raise KeyError(f"instance_id {instance_id} not in verified split")


def get_row_index_map(parquet_path: Path | str = DEFAULT_PARQUET) -> dict[int, int]:
    """Return {instance_id: zero_based_row_index} for the pinned verified split."""
    df = pd.read_parquet(Path(parquet_path).resolve())
    mapping: dict[int, int] = {}
    for idx, row in df.iterrows():
        mapping[int(row["instance_id"])] = int(idx)
    return mapping


# ---------------------------------------------------------------------------
# Evaluator readiness
# ---------------------------------------------------------------------------

class EvaluatorUnavailable(RuntimeError):
    """Raised when the official evaluator cannot run. Fail-closed."""


def check_evaluator_available(
    benchmark_dir: Path | str = DEFAULT_BENCHMARK_DIR,
    upstream_dir: Path | str = DEFAULT_UPSTREAM_DIR,
) -> dict[str, Any]:
    """Return a readiness report; does not raise. Paths are resolved to absolute."""
    bdir = Path(benchmark_dir).resolve()
    udir = Path(upstream_dir).resolve()
    report: dict[str, Any] = {
        "benchmark_dir": str(bdir),
        "benchmark_dir_exists": bdir.exists(),
        "upstream_dir": str(udir),
        "upstream_dir_exists": udir.exists(),
        "eval_programs": (bdir / "eval_programs").exists(),
        "gold_programs": (bdir / "gold_programs").exists(),
        "datasets": (bdir / "datasets").exists(),
        "scoring_rubrics": (bdir / "scoring_rubrics").exists(),
        "docker_harness": (udir / "evaluation" / "harness" / "run_evaluation.py").exists(),
        "run_eval_py": (udir / "run_eval.py").exists(),
    }
    report["ready"] = all(
        report[k]
        for k in (
            "benchmark_dir_exists",
            "eval_programs",
            "gold_programs",
            "datasets",
            "docker_harness",
        )
    )
    return report


# ---------------------------------------------------------------------------
# Official evaluation result
# ---------------------------------------------------------------------------

@dataclass
class OfficialEvalResult:
    task_id: str
    instance_id: int
    row_index: Optional[int]
    official_evaluation: bool
    valid_program: Optional[int]
    codebert_score: Optional[float]
    success_rate: Optional[int]
    log_info: Optional[str]
    raw_output_path: Optional[str]
    eval_jsonl_path: Optional[str]
    execution_evidence_path: Optional[str]
    is_placeholder: Optional[bool]
    error: Optional[str]
    command: Optional[list[str]] = field(default=None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "instance_id": self.instance_id,
            "row_index": self.row_index,
            "official_evaluation": self.official_evaluation,
            "valid_program": self.valid_program,
            "codebert_score": self.codebert_score,
            "success_rate": self.success_rate,
            "log_info": self.log_info,
            "raw_output_path": self.raw_output_path,
            "eval_jsonl_path": self.eval_jsonl_path,
            "execution_evidence_path": self.execution_evidence_path,
            "is_placeholder": self.is_placeholder,
            "error": self.error,
            "command": self.command,
        }


# ---------------------------------------------------------------------------
# JSONL row parsing — R1 critical fix
# ---------------------------------------------------------------------------

def parse_jsonl_row_for_instance(
    jsonl_path: Path | str,
    instance_id: int,
    row_index_map: dict[int, int],
    expected_rows: int = EXPECTED_VERIFIED_ROWS,
) -> dict[str, Any]:
    """Parse the official evaluator JSONL for a specific instance.

    Upstream writes one JSONL line per dataset row (positional).  Rows that were
    not executed are written as placeholder fillers.  This function:
      1. Validates the JSONL has exactly ``expected_rows`` lines.
      2. Maps ``instance_id`` to its zero-based row index via ``row_index_map``.
      3. Returns ONLY that row, tagged with provenance.

    Raises ValueError on any ambiguity, length mismatch, or missing index.
    """
    path = Path(jsonl_path)
    if not path.exists():
        raise ValueError(f"Eval JSONL not found: {path}")

    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(lines) != expected_rows:
        raise ValueError(
            f"Eval JSONL has {len(lines)} rows, expected {expected_rows} "
            f"for the pinned verified split. Refusing to parse."
        )

    if instance_id not in row_index_map:
        raise ValueError(f"instance_id {instance_id} not in pinned verified row-index map")

    idx = row_index_map[instance_id]
    if idx < 0 or idx >= len(lines):
        raise ValueError(f"Row index {idx} for instance {instance_id} out of range")

    try:
        record = json.loads(lines[idx])
    except json.JSONDecodeError as e:
        raise ValueError(f"JSONL row {idx} is malformed: {e}")

    record["_row_index"] = idx
    record["_instance_id"] = instance_id
    record["_total_rows"] = len(lines)
    return record


def detect_placeholder(record: dict[str, Any], execution_evidence_path: Optional[Path]) -> bool:
    """Return True if the JSONL record is a filler / placeholder, not a real evaluation.

    Strategy: a genuine evaluation leaves ``result.json`` in the instance output
    directory (written by ``compute_scores.py`` inside the Docker container).
    A placeholder row has ``valid_program==0`` and no execution evidence file.

    NOTE: A real *failure* also has ``success_rate==0``, so we do NOT use the
    score alone — we require the presence (or absence) of execution evidence.
    """
    if execution_evidence_path is not None and execution_evidence_path.exists():
        return False  # real execution happened
    # No execution evidence → placeholder, even if fields are populated.
    return True


# ---------------------------------------------------------------------------
# Official evaluator invocation
# ---------------------------------------------------------------------------

def _build_command(
    benchmark_dir: Path,
    pred_program_path: Path,
    log_fname: Path,
    upstream_dir: Path,
    run_id: str,
    instance_id: int,
    split: str = PINNED_SPLIT,
) -> list[str]:
    """Build the official evaluator command with absolute paths and pinned split."""
    return [
        "python",
        "-m",
        "evaluation.harness.run_evaluation",
        "--benchmark_path",
        str(benchmark_dir),
        "--pred_program_path",
        str(pred_program_path),
        "--log_fname",
        str(log_fname),
        "--run_id",
        run_id,
        "--split",
        split,
        "--cache_level",
        "base",
        "--max_workers",
        "1",
        "--instance_ids",
        str(instance_id),
    ]


def run_official_evaluation(
    task: TaskMeta,
    pred_program_path: Path | str,
    benchmark_dir: Path | str = DEFAULT_BENCHMARK_DIR,
    upstream_dir: Path | str = DEFAULT_UPSTREAM_DIR,
    output_dir: Path | str = "results/round_001_r1_runs",
    run_id: str = "r1",
    parquet_path: Path | str = DEFAULT_PARQUET,
    timeout_s: int = 3600,
    split: str = PINNED_SPLIT,
) -> OfficialEvalResult:
    """Invoke the official ScienceAgentBench dockerized evaluator for one instance.

    Fail-closed invariants for ``official_evaluation=True``:
      1. Correct pinned split passed on the command line.
      2. All paths are absolute before subprocess launch.
      3. Evaluator process exits 0.
      4. Eval JSONL has exactly ``EXPECTED_VERIFIED_ROWS`` lines.
      5. Target row is selected by row-index map, not "first line with scores".
      6. Execution evidence (result.json) exists for the target instance.
      7. Target row is not a placeholder filler.
      8. Official score fields are populated.

    Any failed invariant → ``official_evaluation=False`` and ``score=None``.
    """
    bdir = Path(benchmark_dir).resolve()
    udir = Path(upstream_dir).resolve()
    pred_path = Path(pred_program_path).resolve()
    outdir = Path(output_dir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    parquet = Path(parquet_path).resolve()

    # -- Invariant 0: artifacts present --
    readiness = check_evaluator_available(bdir, udir)
    if not readiness["ready"]:
        missing = [
            k
            for k in ("eval_programs", "gold_programs", "datasets", "docker_harness")
            if not readiness[k]
        ]
        raise EvaluatorUnavailable(
            "Official ScienceAgentBench evaluator is not runnable. "
            f"Missing: {missing}. Full report: {stable_json(readiness)}. "
            "Download benchmark_verified.zip (password: scienceagentbench) from the "
            "official SharePoint link in the upstream README and unzip under "
            f"{bdir}; clone OSU-NLP-Group/ScienceAgentBench at {udir}."
        )

    # -- Invariant: row-index map from SAME pinned parquet --
    try:
        row_map = get_row_index_map(parquet)
    except Exception as e:
        raise EvaluatorUnavailable(f"Cannot build row-index map from pinned parquet: {e}")

    if task.instance_id not in row_map:
        raise EvaluatorUnavailable(
            f"instance_id {task.instance_id} not in pinned verified split row map"
        )
    row_index = row_map[task.instance_id]

    # -- Build absolute-path command with --split verified --
    log_fname = (outdir / f"{run_id}_{task.task_key}_eval.jsonl").resolve()
    raw_log = (outdir / f"{run_id}_{task.task_key}_eval_raw.json").resolve()
    # Harness writes per-instance evidence under logs/run_evaluation/{run_id}/{instance_id}/
    evidence_path = (
        udir / "logs" / "run_evaluation" / run_id / str(task.instance_id) / "output" / "result.json"
    ).resolve()

    cmd = _build_command(bdir, pred_path, log_fname, udir, run_id, task.instance_id, split)

    # -- Invariant: --split verified must be on the command --
    if "--split" not in cmd or split != PINNED_SPLIT:
        return OfficialEvalResult(
            task_id=task.task_key,
            instance_id=task.instance_id,
            row_index=row_index,
            official_evaluation=False,
            valid_program=None,
            codebert_score=None,
            success_rate=None,
            log_info=None,
            raw_output_path=str(raw_log),
            eval_jsonl_path=str(log_fname),
            execution_evidence_path=str(evidence_path),
            is_placeholder=None,
            error=f"Internal error: split must be '{PINNED_SPLIT}', got '{split}'",
            command=cmd,
        )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(udir) + os.pathsep + env.get("PYTHONPATH", "")

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(udir),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env=env,
        )
    except subprocess.TimeoutExpired as e:
        return OfficialEvalResult(
            task_id=task.task_key,
            instance_id=task.instance_id,
            row_index=row_index,
            official_evaluation=False,
            valid_program=None,
            codebert_score=None,
            success_rate=None,
            log_info=None,
            raw_output_path=str(raw_log),
            eval_jsonl_path=str(log_fname),
            execution_evidence_path=str(evidence_path),
            is_placeholder=None,
            error=f"Evaluator timed out after {timeout_s}s: {e}",
            command=cmd,
        )
    except FileNotFoundError as e:
        raise EvaluatorUnavailable(f"Could not launch official evaluator: {e}")

    # Persist raw stdout/stderr for audit.
    raw_log.write_text(
        json.dumps(
            {
                "cmd": cmd,
                "cwd": str(udir),
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-200_000:],
                "stderr_tail": proc.stderr[-200_000:],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # -- Invariant: process exit code --
    if proc.returncode != 0:
        return OfficialEvalResult(
            task_id=task.task_key,
            instance_id=task.instance_id,
            row_index=row_index,
            official_evaluation=False,
            valid_program=None,
            codebert_score=None,
            success_rate=None,
            log_info=None,
            raw_output_path=str(raw_log),
            eval_jsonl_path=str(log_fname),
            execution_evidence_path=str(evidence_path),
            is_placeholder=None,
            error=f"Evaluator exited with code {proc.returncode}. stderr tail: {proc.stderr[-500:]}",
            command=cmd,
        )

    # -- Invariant: parse JSONL by row index, not "first line with scores" --
    try:
        record = parse_jsonl_row_for_instance(log_fname, task.instance_id, row_map)
    except ValueError as e:
        return OfficialEvalResult(
            task_id=task.task_key,
            instance_id=task.instance_id,
            row_index=row_index,
            official_evaluation=False,
            valid_program=None,
            codebert_score=None,
            success_rate=None,
            log_info=None,
            raw_output_path=str(raw_log),
            eval_jsonl_path=str(log_fname),
            execution_evidence_path=str(evidence_path),
            is_placeholder=None,
            error=f"JSONL row parsing failed: {e}",
            command=cmd,
        )

    # -- Invariant: execution evidence --
    is_placeholder = detect_placeholder(record, evidence_path)

    valid_program = record.get("valid_program")
    codebert = record.get("codebert_score")
    success_rate = record.get("success_rate")
    log_info = record.get("log_info")

    if is_placeholder:
        return OfficialEvalResult(
            task_id=task.task_key,
            instance_id=task.instance_id,
            row_index=row_index,
            official_evaluation=False,
            valid_program=valid_program,
            codebert_score=codebert,
            success_rate=success_rate,
            log_info=log_info,
            raw_output_path=str(raw_log),
            eval_jsonl_path=str(log_fname),
            execution_evidence_path=str(evidence_path),
            is_placeholder=True,
            error=(
                f"Row {row_index} is a placeholder filler (no execution evidence at "
                f"{evidence_path}). Not a genuine evaluation."
            ),
            command=cmd,
        )

    # -- Invariant: score fields populated --
    if success_rate is None or valid_program is None:
        return OfficialEvalResult(
            task_id=task.task_key,
            instance_id=task.instance_id,
            row_index=row_index,
            official_evaluation=False,
            valid_program=valid_program,
            codebert_score=codebert,
            success_rate=success_rate,
            log_info=log_info,
            raw_output_path=str(raw_log),
            eval_jsonl_path=str(log_fname),
            execution_evidence_path=str(evidence_path),
            is_placeholder=False,
            error="Score fields missing from evaluator output despite execution evidence.",
            command=cmd,
        )

    # ALL invariants pass → official_evaluation=True
    return OfficialEvalResult(
        task_id=task.task_key,
        instance_id=task.instance_id,
        row_index=row_index,
        official_evaluation=True,
        valid_program=valid_program,
        codebert_score=codebert,
        success_rate=success_rate,
        log_info=log_info,
        raw_output_path=str(raw_log),
        eval_jsonl_path=str(log_fname),
        execution_evidence_path=str(evidence_path),
        is_placeholder=False,
        error=None,
        command=cmd,
    )
