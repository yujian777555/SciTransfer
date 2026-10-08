import json
from pathlib import Path

import numpy as np
import pandas as pd

data_path = Path("benchmark/datasets/saliva_data/data.pkl")
if not data_path.exists():
    raise FileNotFoundError(f"Dataset not found: {data_path.resolve()}")

df = pd.read_pickle(data_path)

results = {}

for (condition, subject), group in df.groupby(level=["condition", "subject"]):
    cortisol = group["cortisol"]
    sample_index = group.index.get_level_values("sample")

    mean_val = float(cortisol.mean())
    max_location = int(sample_index[np.argmax(cortisol.values)])
    min_location = int(sample_index[np.argmin(cortisol.values)])
    skew_val = float(cortisol.skew())

    results[str(subject)] = {
        "condition": str(condition),
        "mean": mean_val,
        "max_location": max_location,
        "min_location": min_location,
        "skewness": None if np.isnan(skew_val) else skew_val,
    }

output_path = Path("pred_results/saliva_pred.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"Saved features for {len(results)} subjects to {output_path}")