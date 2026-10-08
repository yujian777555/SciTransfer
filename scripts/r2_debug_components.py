"""Debug evaluation components."""
import sys
sys.path.insert(0, "shims")
sys.path.insert(0, "benchmarks/ScienceAgentBench-upstream")

# Test resource shim
import resource
print("resource shim OK")

# Test local dataset adapter
import local_dataset_adapter
print("local adapter OK")

# Test upstream import
from evaluation.harness.run_evaluation import main
print("upstream import OK")

# Test Docker connection
import docker
try:
    client = docker.from_env()
    ver = client.version()
    print(f"Docker OK: {ver.get('Version', 'unknown')}")
except Exception as e:
    print(f"Docker error: {e}")

# Test dataset loading with adapter
print("\nTesting dataset load...")
try:
    from datasets import load_dataset
    ds = load_dataset("osunlp/ScienceAgentBench", split="verified")
    print(f"Loaded {len(ds)} rows")
    ids = [str(row["instance_id"]) for row in ds]
    print(f"Tasks 85, 16, 21 present: {'85' in ids}, {'16' in ids}, {'21' in ids}")
except Exception as e:
    print(f"Dataset load failed: {e}")

print("\nAll components OK.")
