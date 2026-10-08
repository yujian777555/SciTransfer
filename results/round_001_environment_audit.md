# Round 001 Environment Audit

**Date:** 2026-10-08  
**Executor:** MiMo (SciTransfer Executor)  
**OS:** Windows (win32), PowerShell  
**Python:** 3.10.1 (system) / managed `MIMO_PYTHON` available  
**Docker:** 29.3.1  
**Conda:** 23.3.1  

## 1. ScienceAgentBench provenance (verified)

| Item | Value |
|------|-------|
| Upstream repo | https://github.com/OSU-NLP-Group/ScienceAgentBench |
| Upstream commit | `c26e151ed601ba109dc4d35e057ff8e73fec469d` (2026-07-17) |
| HF dataset | `osunlp/ScienceAgentBench` |
| HF dataset SHA | `9c6e96c9e74572e979b0930ee735041cef528cb7` (2026-05-01) |
| Split used | `verified` (102 tasks, released 2026-04-30 to mitigate false negatives) |
| Parquet SHA256 | `c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147` |
| License (tasks) | CC-BY-4.0 (most); retained original for rasterio (32,46,53,54,84) and matminer (3) |
| License (code) | MIT |
| Artifacts | `benchmark_verified.zip` (1,769,478,786 bytes), password `scienceagentbench` |

### Reproducible commands

```bash
# Clone upstream
git clone https://github.com/OSU-NLP-Group/ScienceAgentBench.git ScienceAgentBench-upstream
cd ScienceAgentBench-upstream && git rev-parse HEAD

# Download verified parquet (129 KB)
python -c "import urllib.request; urllib.request.urlretrieve(
  'https://huggingface.co/datasets/osunlp/ScienceAgentBench/resolve/main/data/verified-00000-of-00001.parquet',
  'benchmarks/data/verified-00000-of-00001.parquet')"

# Download full benchmark artifacts (1.77 GB, SharePoint anonymous link)
# URL from upstream README "Benchmark Access" section
curl -L -o benchmark_verified.zip '<SharePoint URL>?download=1'
# Unzip with password: scienceagentbench
# Place contents under: benchmarks/ScienceAgentBench/benchmark/
```

## 2. Verified task split (102 tasks)

| Domain | Count |
|--------|-------|
| Psychology and Cognitive science | 28 |
| Geographical Information Science | 27 |
| Bioinformatics | 27 |
| Computational Chemistry | 20 |

## 3. Selected tasks for Round 001 minimal pilot

| instance_id | Domain | Output type | Rationale |
|-------------|--------|-------------|-----------|
| 85 | Bioinformatics | JSON (`saliva_pred.json`) | Non-visual; avoids GPT-4o judge |
| 16 | Computational Chemistry | Text (`compound_filter_results.txt`) | Non-visual; avoids GPT-4o judge |
| 21 | Geographical Information Science | CSV (`deforestation_rate.csv`) | Non-visual; avoids GPT-4o judge |

All three target domains from the plan are covered. No substitution was needed.

## 4. Evaluator readiness (at time of experiments)

| Component | Status |
|-----------|--------|
| Docker | Available (v29.3.1) |
| Upstream code (`evaluation/harness/`) | Cloned at `../ScienceAgentBench-upstream/` |
| `benchmark/datasets/` | **NOT AVAILABLE** — inside `benchmark_verified.zip`, download in progress |
| `benchmark/eval_programs/` | **NOT AVAILABLE** — same |
| `benchmark/gold_programs/` | **NOT AVAILABLE** — same |
| `benchmark/scoring_rubrics/` | **NOT AVAILABLE** — same |
| Docker harness entry | `python -m evaluation.harness.run_evaluation` (verified in upstream) |
| Official score fields | `valid_program`, `codebert_score`, `success_rate` (0/1), `log_info` |

**Fail-closed behavior verified:** `run_official_evaluation()` raises `EvaluatorUnavailable` when any of the above benchmark folders is missing. Test `test_missing_evaluator_raises_unavailable` passes.

## 5. LLM access

| Key | Status |
|-----|--------|
| `DEEPSEEK_API_KEY` | Working. Models: `deepseek-flash`, `deepseek-v4-pro` |
| `OPENAI_API_KEY` | Same value as `DASHSCOPE_API_KEY`; returns **401** against `api.openai.com`. **Not a valid OpenAI key.** |
| `DASHSCOPE_API_KEY` | Present; DashScope endpoint unreachable from this network (SSL/proxy) |

**Agent model pinned:** `deepseek-v4-pro` via OpenAI-compatible API at `https://api.deepseek.com/v1`.  
This is recorded in every trace. Official SAB `run_infer.py` supports only OpenAI/Bedrock; our harness uses DeepSeek via the OpenAI-compatible chat completions endpoint. Model identity is preserved in `run_result.json` and `trace.jsonl`.

**GPT-4o visual judge:** Blocked (no valid OpenAI key). Selected tasks have non-visual outputs and do not require it.

## 6. Cost accounting

Per-1M-token prices used (documented estimates from DeepSeek pricing page):

| Model | Input | Output |
|-------|-------|--------|
| `deepseek-v4-pro` | $0.50 | $1.50 |

### Observed costs (this round)

| Run | Tokens in | Tokens out | Cost USD |
|-----|-----------|------------|----------|
| sab_verified_85 / NO_STRATEGY | 540 | 3,742 | $0.0059 |
| sab_verified_85 / FIXED_STRATEGY | 762 | 1,997 | $0.0034 |
| sab_verified_16 / NO_STRATEGY | 883 | 5,923 | $0.0093 |
| sab_verified_16 / FIXED_STRATEGY | 1,105 | 5,128 | $0.0082 |
| sab_verified_21 / NO_STRATEGY | 744 | 6,536 | $0.0102 |
| sab_verified_21 / FIXED_STRATEGY | 966 | 6,481 | $0.0102 |
| **Total** | **5,000** | **29,807** | **$0.0472** |

**Projected cost for full official evaluation (3 pairs × 2 arms):** Docker builds + program execution are local compute. GPT-4o visual judge is N/A for selected tasks. Estimated remaining API cost for evaluation: **$0** (no OpenAI calls required for non-visual eval scripts).  
**Projected cost for 2 seeds × 3 domains (if affordable):** ~$0.10 agent cost + local Docker compute.

## 7. Blockers

1. **benchmark_verified.zip download slow/incomplete.** SharePoint link delivers at ~0.1 MB/s with frequent connection drops. Download of 1.77 GB in progress via resumable Python script. **Official evaluation cannot run until this completes and the zip is extracted.**

2. **No valid OpenAI API key.** Required by upstream for GPT-4o visual judge. Not needed for the three selected non-visual tasks, but would block any visualization-output task.

3. **DashScope endpoint unreachable.** SSL/proxy error from this network. DeepSeek is the sole working LLM provider.

## 8. Limitations

- One paired seed per domain (seed 0). Not statistically powered.
- Agent is direct prompting (no self-debug loop) to keep Round 001 bounded.
- Strategy B is a single preregistered generic tactic; no target-task outcome was observed before fixing it.
- `benchmark_verified.zip` SHA256 will be recorded after download completes; per-file dataset checksums require extraction.
- Official evaluation runs are **BLOCKED** in this commit. Once artifacts are available, re-run `python -m scitransfer.cli run-pair --task-id N --seed 0` to obtain genuine official scores.
