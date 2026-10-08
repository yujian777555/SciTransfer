"""Minimal evaluation test: just verify the evaluator can start and load data."""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_DIR = REPO_ROOT / "benchmarks" / "ScienceAgentBench-upstream"
SHIMS_DIR = REPO_ROOT / "shims"

for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ[key] = ""
os.environ["NO_PROXY"] = "*"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

sys.path.insert(0, str(SHIMS_DIR))
sys.path.insert(0, str(UPSTREAM_DIR))

import local_dataset_adapter  # noqa: F401

print("1. Loading dataset...")
sys.stdout.flush()

from datasets import load_dataset
dataset = load_dataset("osunlp/ScienceAgentBench", split="verified")
print(f"   Loaded {len(dataset)} rows")
sys.stdout.flush()

# Find task 85
task_85 = None
for row in dataset:
    if str(row["instance_id"]) == "85":
        task_85 = row
        break

if task_85:
    print(f"   Task 85 found: {task_85['gold_program_name']}")
else:
    print("   Task 85 NOT FOUND")
    sys.exit(1)
sys.stdout.flush()

print("2. Checking Docker...")
sys.stdout.flush()

import docker
client = docker.from_env()
print(f"   Docker: {client.version().get('Version')}")
sys.stdout.flush()

print("3. Building test spec...")
sys.stdout.flush()

from evaluation.harness.test_spec import make_test_spec

BENCHMARK_DIR = str(REPO_ROOT / "benchmarks" / "ScienceAgentBench" / "benchmark")
PRED_DIR = str(REPO_ROOT / "results" / "round_001_r2_runs" / "sab_verified_85__NO_STRATEGY__seed0__eval" / "pred_programs")

test_spec = make_test_spec(task_85, BENCHMARK_DIR, PRED_DIR)
print(f"   Test spec created: {test_spec.instance_id}")
print(f"   Image key: {test_spec.instance_image_key}")
sys.stdout.flush()

print("4. Attempting Docker build (base image)...")
sys.stdout.flush()

from evaluation.harness.docker_build import build_base_images
try:
    build_base_images(client, [task_85], BENCHMARK_DIR, PRED_DIR, force_rebuild=False)
    print("   Base image build completed")
except Exception as e:
    print(f"   Build error: {type(e).__name__}: {e}")
sys.stdout.flush()

print("5. Done.")
