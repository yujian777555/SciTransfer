"""Check additional benchmark candidates."""
import urllib.request, json, ssl

ctx = ssl.create_default_context()

repos = [
    "OpenAI/mle-bench",
    "facebookresearch/mbxp",
    "microsoft/LLMLingua",
    "google/BIG-bench",
    "allenai/ai2thor",
    "Volkswagen/chembench",
    "ur-whitelab/chemcrow",
    "scikit-learn/scikit-learn",
    "huggingface/transformers",
    "stanfordnlp/Core",
    "allenai/olmo-core",
    "jina-ai/jina",
]

for repo in repos:
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}",
            headers={"User-Agent": "sci-transfer"},
        )
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            d = json.load(r)
            lic = d.get("license") or {}
            desc = (d.get("description") or "")[:100]
            print(f"{repo}: stars={d.get('stargazers_count')}, license={lic.get('spdx_id')}, updated={d.get('updated_at','')[:10]}")
            print(f"  {desc}")
    except Exception as e:
        print(f"{repo}: {type(e).__name__}")
