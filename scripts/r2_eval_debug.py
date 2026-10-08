"""Run evaluation with output capture."""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_DIR = REPO_ROOT / "benchmarks" / "ScienceAgentBench-upstream"
BENCHMARK_DIR = REPO_ROOT / "benchmarks" / "ScienceAgentBench" / "benchmark"
SHIMS_DIR = REPO_ROOT / "shims"

for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ[key] = ""
os.environ["NO_PROXY"] = "*"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

sys.path.insert(0, str(SHIMS_DIR))
sys.path.insert(0, str(UPSTREAM_DIR))

import local_dataset_adapter  # noqa: F401

print("Starting evaluation...")
sys.stdout.flush()

from evaluation.harness.run_evaluation import main as upstream_main

pred_dir = Path("results/round_001_r2_runs/sab_verified_85__NO_STRATEGY__seed0__eval/pred_programs").resolve()
output_dir = Path("results/round_001_r2_runs/sab_verified_85__NO_STRATEGY__seed0__eval").resolve()
output_dir.mkdir(parents=True, exist_ok=True)
log_fname = output_dir / "eval_smoke.jsonl"

print(f"Pred dir: {pred_dir}")
print(f"Log: {log_fname}")
sys.stdout.flush()

upstream_main(
    benchmark_path=str(BENCHMARK_DIR),
    pred_program_path=str(pred_dir),
    log_fname=str(log_fname),
    dataset_name="osunlp/ScienceAgentBench",
    split="verified",
    instance_ids=["85"],
    max_workers=1,
    force_rebuild=False,
    cache_level="base",
    clean=False,
    open_file_limit=4096,
    timeout=300,  # 5 min per instance
    run_id="r2_smoke_debug",
    openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
    azure_openai_key="",
    azure_openai_api_version="",
    azure_openai_endpoint="",
    azure_openai_deployment_name="",
)

print("Evaluation complete.")
