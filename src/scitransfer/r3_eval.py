"""R3 evaluation core: direct original scorer invocation with strict A/B isolation.

Key design (per plan_001_r3 Track B):
- Each (task, arm) gets a brand-new isolated workdir
- Full 64-hex SHA256 gate before execution
- No shared pred_results/ between arms
- No stale output reading: require fresh output in THIS run's directory
- Nonzero exit / timeout → score=null, status=EXECUTION_FAILED/TIMEOUT
- Direct import of official scorer eval() functions (not reimplementation)
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = REPO_ROOT / "benchmarks" / "ScienceAgentBench" / "benchmark"
EVAL_PROGRAMS = BENCHMARK / "eval_programs"
GOLD_RESULTS = EVAL_PROGRAMS / "gold_results"
R3_RUNS = REPO_ROOT / "results" / "round_001_r3_runs"
HASH_CATALOG = REPO_ROOT / "results" / "round_001_r1_program_hashes.json"

# Frozen official scorer SHA256 (from preflight)
SCORER_HASHES = {
    85: "31920bb30c6926d2598c00ae8a1bd6d80158ed2afe3ed96ca8bb982f8858ceef",
    16: "216935482b08427dc5c713f4c4b0a83f46eb637846c7f847cfab44cf270bf873",
    21: "c1b2ca7c15c1f2b4ba3520e9d89e35a5656a1c98e63cfac58f63221b46f49819",
}

SCORER_FILES = {
    85: "biopsykit_saliva_eval.py",
    16: "antibioticsai_filter_eval.py",
    21: "eval_deforestation.py",
}

# Provenance categories (plan_001_r3 Track A.5)
PROV_DOCKER = "ORIGINAL_OFFICIAL_DOCKER"
PROV_DIRECT = "DIRECT_ORIGINAL_SCORER_MODIFIED_RUNNER"
PROV_REIMPL = "REIMPLEMENTED_EXPLORATORY"

TIMEOUT_SECONDS = 300  # Same for both arms (plan Track C.2)


@dataclass
class EvalResult:
    task_id: int
    domain: str
    arm: str
    seed: int
    run_id: str
    program_sha256: str
    scorer_sha256: str
    provenance: str
    official_evaluation: bool
    score: Optional[int]
    status: str  # SUCCESS / EXECUTION_FAILED / TIMEOUT / HASH_MISMATCH / ERROR
    exit_code: Optional[int]
    duration_s: float
    output_path: Optional[str]
    output_sha256: Optional[str]
    error: Optional[str]
    log_info: Optional[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": f"sab_verified_{self.task_id}",
            "instance_id": self.task_id,
            "domain": self.domain,
            "arm": self.arm,
            "seed": self.seed,
            "run_id": self.run_id,
            "program_sha256": self.program_sha256,
            "scorer_sha256": self.scorer_sha256,
            "provenance": self.provenance,
            "official_evaluation": self.official_evaluation,
            "modified_evaluator": self.provenance != PROV_DOCKER,
            "score": self.score,
            "success_rate": self.score,
            "status": self.status,
            "exit_code": self.exit_code,
            "duration_s": round(self.duration_s, 3),
            "output_path": self.output_path,
            "output_sha256": self.output_sha256,
            "error": self.error,
            "log_info": self.log_info,
        }


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen_hashes() -> dict[str, str]:
    """Load full SHA256 catalog. Keys are run names, values are full hex."""
    data = json.loads(HASH_CATALOG.read_text(encoding="utf-8"))
    # Handle both dict-of-dict and dict-of-string formats
    result = {}
    for k, v in data.items():
        if isinstance(v, dict):
            result[k] = v.get("sha256", "")
        else:
            result[k] = str(v)
    return result


def verify_program_hash(program_path: Path, expected_full_sha: str) -> bool:
    """Full 64-hex comparison. FAIL CLOSED on mismatch."""
    actual = sha256_file(program_path)
    return actual == expected_full_sha


def load_official_scorer(task_id: int):
    """Directly import the official scorer module. Returns the module with eval()."""
    scorer_file = EVAL_PROGRAMS / SCORER_FILES[task_id]
    if not scorer_file.exists():
        raise FileNotFoundError(f"Official scorer not found: {scorer_file}")

    # Verify scorer file hash
    actual_hash = sha256_file(scorer_file)
    if actual_hash != SCORER_HASHES[task_id]:
        raise RuntimeError(
            f"Scorer hash mismatch for task {task_id}: "
            f"expected {SCORER_HASHES[task_id][:16]}..., got {actual_hash[:16]}..."
        )

    # Import as module
    mod_name = f"_official_scorer_{task_id}"
    spec = importlib.util.spec_from_file_location(mod_name, scorer_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load scorer spec: {scorer_file}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)

    if not hasattr(mod, "eval"):
        raise AttributeError(f"Scorer module has no eval() function: {scorer_file}")

    return mod, actual_hash


def prepare_isolated_workdir(task_id: int, arm: str, seed: int, program_path: Path) -> tuple[Path, Path]:
    """Create a brand-new isolated workdir. Returns (workdir, staged_program).

    Layout inside workdir:
      workdir/
        pred_results/          <- program writes output here
        benchmark/             <- symlink/junction to read-only data
          datasets/...
          eval_programs/
            gold_results/...
            <scorer>.py
    """
    run_id = f"r3_{task_id}_{arm.lower()}_s{seed}"
    workdir = R3_RUNS / run_id

    # Fail if already exists (no reuse, no stale output)
    if workdir.exists():
        raise FileExistsError(
            f"Run dir already exists (refusing to reuse): {workdir}. "
            f"Delete it manually or use a new seed."
        )

    workdir.mkdir(parents=True)
    (workdir / "pred_results").mkdir()

    # Create benchmark/ junction for data access (read-only by convention)
    bench_link = workdir / "benchmark"
    # On Windows, create junction to the real benchmark dir
    import subprocess as sp
    result = sp.run(
        ["cmd", "/c", "mklink", "/J", str(bench_link), str(BENCHMARK)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create benchmark junction: {result.stderr}")

    # Stage program with exact expected name
    gold_names = {
        85: "saliva.py",
        16: "compound_filter.py",
        21: "deforestation.py",
    }
    staged_name = "pred_" + gold_names[task_id]
    staged = workdir / staged_name
    shutil.copy2(program_path, staged)

    # Re-hash staged copy (integrity)
    source_hash = sha256_file(program_path)
    staged_hash = sha256_file(staged)
    if source_hash != staged_hash:
        raise RuntimeError(f"Staged copy hash mismatch: {source_hash} vs {staged_hash}")

    return workdir, staged


def run_program_isolated(workdir: Path, staged_program: Path, timeout_s: int = TIMEOUT_SECONDS):
    """Run program in isolated workdir. Returns (exit_code, stdout, stderr, timed_out, duration)."""
    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, str(staged_program)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=str(workdir),  # Program runs in isolated dir; pred_results/ is here
        )
        duration = time.time() - t0
        return proc.returncode, proc.stdout, proc.stderr, False, duration
    except subprocess.TimeoutExpired as e:
        duration = time.time() - t0
        # Capture partial output
        stdout = e.stdout.decode("utf-8", errors="replace") if e.stdout else ""
        stderr = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
        return -1, stdout, stderr, True, duration


def find_output(workdir: Path, task_id: int) -> Optional[Path]:
    """Find the expected output file in THIS workdir's pred_results/."""
    output_names = {
        85: "saliva_pred.json",
        16: "compound_filter_results.txt",
        21: "deforestation_rate.csv",
    }
    output_path = workdir / "pred_results" / output_names[task_id]
    return output_path if output_path.exists() else None


def score_with_original(task_id: int, workdir: Path) -> tuple[Optional[int], str]:
    """Invoke the OFFICIAL scorer's eval() function directly.

    The scorer expects paths relative to CWD:
      - benchmark/eval_programs/gold_results/... (via junction)
      - pred_results/... (in workdir)

    We change CWD to workdir so the scorer finds files at its expected paths.

    Exceptions propagate to caller (official harness catches and returns 0).
    """
    mod, scorer_hash = load_official_scorer(task_id)

    # Save and restore CWD
    old_cwd = os.getcwd()
    try:
        os.chdir(str(workdir))
        result = mod.eval()
        if isinstance(result, tuple) and len(result) == 2:
            score, log_info = result
            return int(score), str(log_info)
        else:
            return None, f"Unexpected eval() return: {result!r}"
    finally:
        os.chdir(old_cwd)


def evaluate_one(task_id: int, arm: str, seed: int = 0) -> EvalResult:
    """Full evaluation pipeline for one (task, arm, seed)."""
    domains = {
        85: "Bioinformatics",
        16: "Computational Chemistry",
        21: "Geographical Information Science",
    }
    run_id = f"r3_{task_id}_{arm.lower()}_s{seed}"

    # 1. Load frozen hash and verify FULL SHA256
    hashes = load_frozen_hashes()
    run_key = f"sab_verified_{task_id}__{arm}__seed{seed}"
    expected_sha = hashes.get(run_key, "")

    source_dir = REPO_ROOT / "results" / "round_001_runs" / run_key
    pred_files = list(source_dir.glob("pred_*.py"))
    if not pred_files:
        return EvalResult(
            task_id=task_id, domain=domains[task_id], arm=arm, seed=seed,
            run_id=run_id, program_sha256="", scorer_sha256="",
            provenance=PROV_DIRECT, official_evaluation=False,
            score=None, status="ERROR", exit_code=None, duration_s=0,
            output_path=None, output_sha256=None,
            error=f"Program not found in {source_dir}", log_info=None,
        )

    program_path = pred_files[0]
    actual_sha = sha256_file(program_path)

    # HARD GATE: full 64-hex comparison
    if not verify_program_hash(program_path, expected_sha):
        return EvalResult(
            task_id=task_id, domain=domains[task_id], arm=arm, seed=seed,
            run_id=run_id, program_sha256=actual_sha, scorer_sha256="",
            provenance=PROV_DIRECT, official_evaluation=False,
            score=None, status="HASH_MISMATCH", exit_code=None, duration_s=0,
            output_path=None, output_sha256=None,
            error=f"Full SHA mismatch: expected {expected_sha[:16]}..., got {actual_sha[:16]}...",
            log_info=None,
        )

    # 2. Prepare isolated workspace
    try:
        workdir, staged = prepare_isolated_workdir(task_id, arm, seed, program_path)
    except (FileExistsError, RuntimeError) as e:
        return EvalResult(
            task_id=task_id, domain=domains[task_id], arm=arm, seed=seed,
            run_id=run_id, program_sha256=actual_sha, scorer_sha256="",
            provenance=PROV_DIRECT, official_evaluation=False,
            score=None, status="ERROR", exit_code=None, duration_s=0,
            output_path=None, output_sha256=None,
            error=str(e), log_info=None,
        )

    # 3. Run program in isolation
    exit_code, stdout, stderr, timed_out, duration = run_program_isolated(workdir, staged)

    # Save stdout/stderr
    (workdir / "stdout.txt").write_text(stdout or "", encoding="utf-8")
    (workdir / "stderr.txt").write_text(stderr or "", encoding="utf-8")

    # 4. Check execution result
    if timed_out:
        return EvalResult(
            task_id=task_id, domain=domains[task_id], arm=arm, seed=seed,
            run_id=run_id, program_sha256=actual_sha, scorer_sha256="",
            provenance=PROV_DIRECT, official_evaluation=False,
            score=None, status="TIMEOUT", exit_code=exit_code, duration_s=duration,
            output_path=None, output_sha256=None,
            error=f"Timeout after {TIMEOUT_SECONDS}s", log_info=None,
        )

    if exit_code != 0:
        return EvalResult(
            task_id=task_id, domain=domains[task_id], arm=arm, seed=seed,
            run_id=run_id, program_sha256=actual_sha, scorer_sha256="",
            provenance=PROV_DIRECT, official_evaluation=False,
            score=None, status="EXECUTION_FAILED", exit_code=exit_code, duration_s=duration,
            output_path=None, output_sha256=None,
            error=f"Nonzero exit {exit_code}: {stderr[:200] if stderr else 'no stderr'}",
            log_info=None,
        )

    # 5. Find fresh output in THIS workdir only
    output_path = find_output(workdir, task_id)
    if output_path is None:
        return EvalResult(
            task_id=task_id, domain=domains[task_id], arm=arm, seed=seed,
            run_id=run_id, program_sha256=actual_sha, scorer_sha256="",
            provenance=PROV_DIRECT, official_evaluation=False,
            score=None, status="EXECUTION_FAILED", exit_code=exit_code, duration_s=duration,
            output_path=None, output_sha256=None,
            error="No fresh output in isolated workdir", log_info=None,
        )

    output_sha = sha256_file(output_path)

    # 6. Score with ORIGINAL official scorer
    try:
        score, log_info = score_with_original(task_id, workdir)
        scorer_hash = SCORER_HASHES[task_id]
    except Exception as e:
        # Official harness (compute_scores.py) catches scorer exceptions
        # and returns score=0 (invalid output = failure). Match that behavior.
        return EvalResult(
            task_id=task_id, domain=domains[task_id], arm=arm, seed=seed,
            run_id=run_id, program_sha256=actual_sha, scorer_sha256=SCORER_HASHES[task_id],
            provenance=PROV_DIRECT, official_evaluation=False,
            score=0, status="SUCCESS", exit_code=exit_code, duration_s=duration,
            output_path=str(output_path), output_sha256=output_sha,
            error=f"Scorer exception (official harness would return 0): {e}",
            log_info=f"EXCEPTION: {e}",
        )

    return EvalResult(
        task_id=task_id, domain=domains[task_id], arm=arm, seed=seed,
        run_id=run_id, program_sha256=actual_sha, scorer_sha256=scorer_hash,
        provenance=PROV_DIRECT, official_evaluation=False,
        score=score, status="SUCCESS" if score is not None else "ERROR",
        exit_code=exit_code, duration_s=duration,
        output_path=str(output_path), output_sha256=output_sha,
        error=None, log_info=log_info,
    )
