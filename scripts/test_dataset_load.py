"""Test dataset loading with proxy disabled."""
import os
import sys

# Disable proxy
for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ[key] = ""
os.environ["NO_PROXY"] = "*"
os.environ["HF_ENDPOINT"] = "https://huggingface.co"

print("Testing dataset load without proxy...")
try:
    from datasets import load_dataset
    ds = load_dataset("osunlp/ScienceAgentBench", split="verified")
    print(f"Loaded {len(ds)} rows")
    first_id = ds[0]["instance_id"]
    print(f"First instance_id: {first_id}")
    # Check tasks 85, 16, 21 are present
    ids = set(str(row["instance_id"]) for row in ds)
    for t in ["85", "16", "21"]:
        print(f"  Task {t} in dataset: {t in ids}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
    sys.exit(1)
