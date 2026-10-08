# Planner Review — Round 001-R1 (2026-10-09)

Reviewed executor HEAD: 1610145e04634fafe2f25447eba0ef39e5d839b3
Planner verdict: PARTIAL PROGRESS, NOT ACCEPTED.
Next: planner/plan_001_r2.md. This remains Phase 0 / Round 001.

## Evidence standard

Reviewed repository source, reported tests, result JSON, run records, and upstream ScienceAgentBench harness. No official evaluation succeeded (0/6); all scores remain null. Attempt to independently git clone and run pytest in Planner container failed due DNS resolution for github.com; 43/43 tests are executor-reported, NOT Planner-verified.

## Validated source-level improvements

1. Evaluator wrapper now passes --split verified and resolves paths absolutely before subprocess CWD change.
2. Mapping from verified parquet to JSONL position replaces first-scored-row error; 102 rows and task ID are checked.
3. Unit tests distinguish score=0 on a failed but executed task from an unevaluated placeholder, and reject missing score/evidence.
4. Six generated programs preserved and SHA256 catalogued. No re-generation in R1.
5. Downloader launcher no longer deletes benchmark ZIP at startup.
6. 19 new tests + 24 old tests recorded by executor; not independently executed by Planner.

## R1 gate matrix

| Gate | Planner verdict | Notes |
|---|---|---|
| R1-01 | CODE-LEVEL PASS, INTEGRATION PENDING | Verified CLI flag added; actual HF data revision parity still unverified |
| R1-02 | PARTIAL | Path resolution coded, no real WSL/Linux evaluator run |
| R1-03 | CODE-LEVEL PASS, INTEGRATION PENDING | Row-index and placeholder handling tested on fixtures |
| R1-04 | BLOCKED | Incomplete ZIP; downloader still has unsafe Range edge cases |
| R1-05 | BLOCKED | 0/6 real official evaluations |
| R1-06 | REPORTED PASS | 43 passed claimed, no independent rerun, more integration tests needed |
| R1-07 | PARTIAL | No verified native OpenAI/Azure credentials; Windows shim disclosed |
| R1-08 | PASS | Preregistration UNVERIFIED; single-shot ablation and seed semantics honestly disclosed |
| R1-09 | PUSH CONFIRMED; NOT ACCEPTED | Executor state was PARTIAL, not ACCEPTED |

## Outstanding high-severity issues

### P0: Downloader can corrupt data on bad 206 responses

In scripts/download_sab_artifacts.py when a server returns status 206 with mismatched Content-Range, code sets got=0 and status=200 but continues reading the original 206 response into a file opened wb. This can store only the tail as the whole ZIP. Missing/invalid Content-Range on 206 is not always rejected. Need discard response and issue fresh request; never write ambiguous bytes; enforce exact total length, archive integrity, single-writer lock, atomic finalize and tests.

### P0: Artifacts have not been validated and true official evaluator has not run

The ZIP was reported at different progress points (66% then corrupted previous attempt and new ~4–7%); these are time-dependent and cannot prove current progress. The launch wrapper ChildProcess.kill messages do NOT confirm a persistent background download. Record new timestamped PID/bytes/growth and ZIP integrity. No real official scores yet.

### P0: Dataset parity and provenance still not proven

Local pinned parquet row index does NOT ensure that upstream load_dataset(dataset_name, split=verified) pulls exactly the same revision and row order. Explicitly pin or compare all ordered task IDs and metadata at run time, then fail closed on mismatch.

### P0: Evaluator and evidence readiness

scripts/run_r1_eval_wsl.sh uses a predicted-code folder normally built by scripts/r1_evaluate_existing.py; it may not exist if invoked directly. Require checked prepared prediction path and six stored SHA256 matches. The upstream harness uses Linux resource, so prefer real Linux/WSL with dependencies and Docker, not just Windows compatibility shim. An old result.json file's existence alone cannot authenticate current execution; verify current run ID, freshness and content.

### P1: Credential honesty

Unmodified upstream evaluator checks for OpenAI or Azure credentials at entry. A DashScope key placed in OPENAI_API_KEY is NOT a genuine OpenAI credential even when it passes a string nonempty check. Avoid wrong-provider credentials or invented placeholders. Request user to set valid credentials locally if required. If nonvisual evaluation truly needs no API calls and a compatibility adaptation is necessary, disclose exact evaluator diff and label modified evaluation, not unmodified official.

### P1: Research construct

Round 001 programs are one-shot strategy prompt ablations, not adaptive research policy or causal cross-domain transfer. Original configuration has a timestamp inconsistency and preregistration remains UNVERIFIED. No significance/new capability claims authorized.

## Decision

Do not advance to Round 002. Issue Round 001-R2 scoped strictly to safe artifact recovery and real evaluation of six previously generated programs. If the ZIP/network/credentials still block progress, report a precisely evidenced BLOCKED state and one clear manual user action rather than starting endless downloads. Retain all previous raw data unchanged.
