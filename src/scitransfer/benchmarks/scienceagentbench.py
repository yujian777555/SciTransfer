"""ScienceAgentBench loader and official evaluator interface.

Fails closed when the verified evaluator or its artifacts are missing.
Never fabricates scores.
"""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from ..core.types import sha256_of, stable_json


DEFAULT_PARQUET = Path("benchmarks/data/verified-00000-of-00001.parquet")
DEFAULT_BENCHMARK_DIR = Path("benchmarks/ScienceAgentBench/benchmark")
DEFAULT_UPSTREAM_DIR = Path("benchmarks/ScienceAgentBench-upstream")


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


def load_verified_tasks(parquet_path: Path | str = DEFAULT_PARQUET) -> list[TaskMeta]:
    """Load the official verified split (102 tasks)."""
    path = Path(parquet_path)
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


class EvaluatorUnavailable(RuntimeError):
    """Raised when the official evaluator cannot run. Fail-closed."""


@dataclass
class OfficialEvalResult:
    task_id: str
    instance_id: int
    official_evaluation: bool
    valid_program: Optional[int]
    codebert_score: Optional[float]
    success_rate: Optional[int]
    log_info: Optional[str]
    raw_output_path: Optional[str]
    error: Optional[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "instance_id": self.instance_id,
            "official_evaluation": self.official_evaluation,
            "valid_program": self.valid_program,
            "codebert_score": self.codebert_score,
            "success_rate": self.success_rate,
            "log_info": self.log_info,
            "raw_output_path": self.raw_output_path,
            "error": self.error,
        }


def check_evaluator_available(
    benchmark_dir: Path | str = DEFAULT_BENCHMARK_DIR,
    upstream_dir: Path | str = DEFAULT_UPSTREAM_DIR,
) -> dict[str, Any]:
    """Return a readiness report; does not raise."""
    bdir = Path(benchmark_dir)
    udir = Path(upstream_dir)
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


def run_official_evaluation(
    task: TaskMeta,
    pred_program_path: Path | str,
    benchmark_dir: Path | str = DEFAULT_BENCHMARK_DIR,
    upstream_dir: Path | str = DEFAULT_UPSTREAM_DIR,
    output_dir: Path | str = "results/round_001_runs",
    run_id: str = "round_001",
    timeout_s: int = 1800,
) -> OfficialEvalResult:
    """Invoke the official ScienceAgentBench dockerized evaluator for one instance.

    Fail-closed: raises EvaluatorUnavailable if artifacts/harness are missing,
    or returns a result with official_evaluation=False and an error string if
    the evaluator itself fails. Never invents a score.
    """
    bdir = Path(benchmark_dir)
    udir = Path(upstream_dir)
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    readiness = check_evaluator_available(bdir, udir)
    if not readiness["ready"]:
        missing = [k for k in ("eval_programs", "gold_programs", "datasets", "docker_harness") if not readiness[k]]
        raise EvaluatorUnavailable(
            "Official ScienceAgentBench evaluator is not runnable. "
            f"Missing: {missing}. Full report: {stable_json(readiness)}. "
            "Download benchmark_verified.zip (password: scienceagentbench) from the "
            "official SharePoint link in the upstream README and unzip under "
            f"{bdir}; clone OSU-NLP-Group/ScienceAgentBench at {udir}."
        )

    pred_path = Path(pred_program_path)
    log_fname = outdir / f"{run_id}_{task.task_key}_eval.jsonl"
    raw_log = outdir / f"{run_id}_{task.task_key}_eval_raw.jsonl"

    cmd = [
        "python",
        "-m",
        "evaluation.harness.run_evaluation",
        "--benchmark_path",
        str(bdir),
        "--pred_program_path",
        str(pred_path),
        "--log_fname",
        str(log_fname),
        "--run_id",
        run_id,
        "--cache_level",
        "base",
        "--max_workers",
        "1",
        "--instance_ids",
        str(task.instance_id),
    ]

    env = os.environ.copy()
    # Official harness needs PYTHONPATH for relative imports.
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
            official_evaluation=False,
            valid_program=None,
            codebert_score=None,
            success_rate=None,
            log_info=None,
            raw_output_path=None,
            error=f"Evaluator timed out after {timeout_s}s: {e}",
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
                "stdout": proc.stdout[-200_000:],
                "stderr": proc.stderr[-200_000:],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # Parse official JSONL log for this instance.
    valid_program = codebert = success_rate = log_info = None
    if log_fname.exists():
        for line in log_fname.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            # Harness writes per-instance records; match on any score fields.
            if "success_rate" in rec or "valid_program" in rec:
                valid_program = rec.get("valid_program")
                codebert = rec.get("codebert_score")
                success_rate = rec.get("success_rate")
                log_info = rec.get("log_info")
                break

    if proc.returncode != 0 and success_rate is None:
        return OfficialEvalResult(
            task_id=task.task_key,
            instance_id=task.instance_id,
            official_evaluation=False,
            valid_program=valid_program,
            codebert_score=codebert,
            success_rate=success_rate,
            log_info=log_info,
            raw_output_path=str(raw_log),
            error=f"Evaluator exited with code {proc.returncode}. stderr tail: {proc.stderr[-500:]}",
        )

    return OfficialEvalResult(
        task_id=task.task_key,
        instance_id=task.instance_id,
        official_evaluation=True,
        valid_program=valid_program,
        codebert_score=codebert,
        success_rate=success_rate,
        log_info=log_info,
        raw_output_path=str(raw_log),
        error=None,
    )
