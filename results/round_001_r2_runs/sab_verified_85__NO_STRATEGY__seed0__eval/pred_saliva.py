import json
from pathlib import Path

import pandas as pd

# Load the saliva dataset
data_path = Path("benchmark/datasets/saliva_data/data.pkl")
df = pd.read_pickle(data_path)

# Compute features for each subject
results = {}

for (condition, subject), group in df.groupby(level=["condition", "subject"]):
    sub = group.reset_index()
    cortisol = sub["cortisol"]

    results[str(subject)] = {
        "condition": str(condition),
        "mean": float(cortisol.mean()),
        "std": float(cortisol.std()),
        "median": float(cortisol.median()),
        "min": float(cortisol.min()),
        "max": float(cortisol.max()),
        "loc_min": int(sub.loc[cortisol.idxmin(), "sample"]),
        "loc_max": int(sub.loc[cortisol.idxmax(), "sample"]),
        "skewness": float(cortisol.skew()),
        "kurtosis": float(cortisol.kurtosis()),
    }

# Save results as JSON
output_dir = Path("pred_results")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "saliva_pred.json"

with open(output_path, "w") as f:
    json.dump(results, f, indent=2)