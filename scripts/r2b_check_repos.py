"""Check candidate benchmark repos."""
import urllib.request, json, ssl

ctx = ssl.create_default_context()

repos = [
    "allenai/discoveryworld",
    "OSU-NLP-Group/ScienceAgentBench",
    "OSU-NLP-Group/SciAgentGym",
    "scagentgym/SciAgentGym",
    "OpenPipe/ART",
    "Farama-Foundation/TextWorld",
]

for repo in repos:
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}",
            headers={"User-Agent": "sci-transfer"},
        )
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            d = json.load(r)
            lic = d.get("license") or {}
            print(f"{repo}:")
            print(f"  stars={d.get('stargazers_count')}, license={lic.get('spdx_id')}, updated={d.get('updated_at','')[:10]}")
            print(f"  desc: {(d.get('description') or '')[:120]}")
    except Exception as e:
        print(f"{repo}: ERROR {type(e).__name__}: {e}")
