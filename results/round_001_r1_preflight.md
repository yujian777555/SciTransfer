# Round 001-R1 Preflight Report

**Date:** 2026-10-08 (UTC+8)  
**Executor:** MiMo (SciTransfer Executor, R1 remediation)  
**Plan:** `planner/plan_001_r1.md`  
**Platform:** Windows 10/11 (win32), PowerShell 5.1  
**Python:** 3.10.1 (system)  
**Docker Desktop:** installed, **currently Stopped**  
**WSL2:** Ubuntu-22.04 installed, **currently Stopped**  

## 1. Upstream evaluator behavior (inspected at `c26e151`)

### 1.1 `import resource` — Unix-only

`evaluation/harness/run_evaluation.py` line 6: `import resource` — this module does not exist on native Windows Python (`ModuleNotFoundError`). Additionally `resource.setrlimit(resource.RLIMIT_NOFILE, ...)` is called in `main()`.

**Impact:** The official harness cannot run under native Windows Python.  
**Mitigation:** Run under WSL2 Ubuntu-22.04 or Linux Docker container. WSL2 is available.

### 1.2 OpenAI/Azure credential preflight — unconditional

In `main()` (around line 230), the harness raises `ValueError` if neither `OPENAI_API_KEY` nor full Azure credentials are set. This happens **before** any task is selected or evaluated.

**Impact:** Even for non-visual tasks (our 85/16/21), the unmodified harness requires a valid OpenAI or Azure credential to start.  
**Evidence:**
```python
if openai_api_key == "":
    if (azure_openai_key == "" or azure_openai_endpoint == "" or ...):
        raise ValueError("Please provide either OpenAI API key (OPENAI_API_KEY) or Azure OpenAI credentials ...")
```

**Current environment:** `OPENAI_API_KEY` is set to a DashScope key (`sk-4235...`), which returns HTTP 401 against `api.openai.com`. `DEEPSEEK_API_KEY` is available but is not OpenAI/Azure.

**Decision:** Do NOT use DashScope key as OpenAI key. Do NOT inject fake placeholder credentials. If a valid OpenAI/Azure key is required for unmodified evaluation, request user to configure one locally. If we must proceed without it, any adaptation will be labeled as a **modified evaluator fork** with explicit disclosure.

### 1.3 `--split` defaults to `validation`

`run_evaluation.py` parser: `parser.add_argument("--split", type=str, default="validation", ...)`. The verified split is `"verified"`. **R1 fix:** explicitly pass `--split verified` (implemented and tested).

### 1.4 JSONL output format — one line per dataset row

The harness writes `evaluated_logs` (length = dataset size) as one JSONL line per row. Unevaluated rows get placeholder fillers: `{"valid_program": 0, "codebert_score": <default>, "success_rate": 0, "log_info": <default>}`. Lines do NOT contain `instance_id` — they are positional.

**R1 fix:** Parse by row-index mapping from the pinned verified parquet. Validate line count = 102. Use execution evidence (`result.json`) to distinguish real failures from placeholders. (Implemented and tested.)

### 1.5 Absolute paths

R1 fix: all paths resolved to `Path.resolve()` before subprocess launch. Command and cwd use absolute paths. (Implemented and tested.)

## 2. Expected evaluator command (R1)

```bash
# Run under WSL2 Ubuntu-22.04 (where `resource` module exists)
cd /path/to/ScienceAgentBench-upstream
PYTHONPATH=. python -m evaluation.harness.run_evaluation \
    --benchmark_path /abs/path/to/benchmark \
    --pred_program_path /abs/path/to/pred_programs \
    --log_fname /abs/path/to/eval_output.jsonl \
    --run_id r1_{arm}_s{seed}_i{instance_id} \
    --split verified \
    --cache_level base \
    --max_workers 1 \
    --instance_ids {instance_id}
```

## 3. Credential strategy

| Credential | Status | Usable for official harness? |
|------------|--------|------------------------------|
| `DEEPSEEK_API_KEY` | Working | No (not OpenAI/Azure) |
| `OPENAI_API_KEY` (= DashScope) | 401 on api.openai.com | No |
| `DASHSCOPE_API_KEY` | Endpoint unreachable | No |
| Azure OpenAI | Not configured | No |

**Action:** If the user has a valid OpenAI/Azure key, they should set it locally (not in chat or Git). The harness will then proceed. If not, we document BLOCKED with this exact evidence.

## 4. ZIP download status

| Item | Value |
|------|-------|
| File | `sab-artifacts/benchmark_verified.zip` |
| Expected size | 1,769,478,786 bytes |
| Current size | ~1,168,722,513 bytes (~66%) |
| Resume method | HTTP Range with Content-Range offset validation (R1 fix) |
| Download script | `scripts/download_sab_artifacts.py` (non-destructive) |
| Starter script | `scripts/start_download.ps1` (R1 fix: no Remove-Item) |

## 5. Docker/WSL readiness

| Component | Status |
|-----------|--------|
| Docker Desktop | Installed, Stopped |
| WSL Ubuntu-22.04 | Installed, Stopped |
| Docker in WSL | Requires Docker Desktop WSL integration |
| Network for image builds | TBD (will record exact errors) |

## 6. Test summary (E0)

```
python -m pytest tests/ -v
→ 43 passed, 0 failed, 0 skipped
```

- 19 R1 evaluator integrity tests (split, paths, JSONL parsing, placeholder, fail-closed, downloader safety)
- 24 original Round 001 safeguard tests

## 7. Relabeling notes (D1–D4 of plan)

- **Preregistration timestamp:** `preregistered_at=2026-10-08T22:00:00Z` conflicts with run timestamps ~14:44Z. This is likely a timezone error (UTC+8 local time recorded as UTC). **Status: UNVERIFIED.** Original config preserved unchanged.
- **A/B arm label:** The current experiment is a **single-shot strategy prompt ablation** (one model call per arm), NOT an executed adaptive research policy. Any future iterative strategy requires actual code execution/feedback loops.
- **Seed semantics:** `seed=0` is a pairing label only. DeepSeek API at temperature=0 does not guarantee deterministic sampling (no provider seed parameter is passed). This is honest model stochasticity, not a flaw in the pairing.
- **R1 scoring mode:** Retrospective scoring of existing Round 001 generated programs. NOT a new pre-registered trial.
