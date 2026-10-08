"""Run official ScienceAgentBench evaluator with local dataset adapter.

DISCLOSED ADAPTATION:
- Uses local pinned parquet instead of HuggingFace Hub (network unreachable)
- Uses resource.py shim on Windows (upstream requires Unix-only module)
- These are I/O and platform adapters, NOT evaluation logic modifications.

All scoring, Docker execution, JSONL output are identical to unmodified upstream.
"""
import os
import sys
from pathlib import Path

# Set up paths
REPO_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_DIR = REPO_ROOT / "benchmarks" / "ScienceAgentBench-upstream"
BENCHMARK_DIR = REPO_ROOT / "benchmarks" / "ScienceAgentBench" / "benchmark"
SHIMS_DIR = REPO_ROOT / "shims"

# Configure environment BEFORE importing upstream code
for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ[key] = ""
os.environ["NO_PROXY"] = "*"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

# Insert shims (resource.py) and upstream to path
sys.path.insert(0, str(SHIMS_DIR))
sys.path.insert(0, str(UPSTREAM_DIR))

# Apply local dataset adapter
import local_dataset_adapter  # noqa: F401 (patches datasets.load_dataset)

# Now import and run the upstream evaluator
from evaluation.harness.run_evaluation import main as upstream_main

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--instance-id", type=int, required=True)
    parser.add_argument("--pred-dir", type=str, required=True)
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--run-id", type=str, required=True)
    parser.add_argument("--arm", type=str, default="unknown")
    args = parser.parse_args()

    pred_dir = Path(args.pred_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    log_fname = output_dir / f"{args.run_id}_eval.jsonl"

    print(f"=== R2 Official Evaluation (disclosed adapters) ===")
    print(f"  Instance: {args.instance_id}")
    print(f"  Arm: {args.arm}")
    print(f"  Pred dir: {pred_dir}")
    print(f"  Log: {log_fname}")
    print(f"  Run ID: {args.run_id}")
    print(f"  Split: verified")
    print(f"  Adapters: local_dataset_adapter (HF offline), resource shim (Windows)")

    # Call upstream main with proper arguments
    upstream_main(
        benchmark_path=str(BENCHMARK_DIR),
        pred_program_path=str(pred_dir),
        log_fname=str(log_fname),
        dataset_name="osunlp/ScienceAgentBench",
        split="verified",
        instance_ids=[str(args.instance_id)],
        max_workers=1,
        force_rebuild=False,
        cache_level="base",
        clean=False,
        open_file_limit=4096,
        timeout=1800,
        run_id=args.run_id,
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        azure_openai_key="",
        azure_openai_api_version="",
        azure_openai_endpoint="",
        azure_openai_deployment_name="",
    )

    print(f"\n=== Evaluation complete ===")
    print(f"Check log: {log_fname}")
    evidence = UPSTREAM_DIR / "logs" / "run_evaluation" / args.run_id / str(args.instance_id) / "output" / "result.json"
    print(f"Check evidence: {evidence}")
