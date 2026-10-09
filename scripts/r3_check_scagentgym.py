import urllib.request, json, ssl
ctx = ssl.create_default_context()
req = urllib.request.Request('https://api.github.com/repos/CMarsRover/SciAgentGYM', headers={'User-Agent': 'sci-transfer'})
with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
    d = json.load(r)
    lic = d.get('license') or {}
    print(f"Repo: {d['full_name']}")
    print(f"Stars: {d['stargazers_count']}")
    print(f"License: {lic.get('spdx_id', 'none')}")
    print(f"Default branch: {d['default_branch']}")
    print(f"Updated: {d['updated_at']}")
    print(f"Description: {d.get('description', '')}")
    print(f"Clone URL: {d['clone_url']}")
    print(f"Size: {d['size']} KB")
