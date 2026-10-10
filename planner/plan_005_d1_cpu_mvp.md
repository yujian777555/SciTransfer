# SciTransfer — Planner Round 005: D1 Scientific Measurement CPU MVP

**Issued:** 2026-10-10
**Planner:** ChatGPT; **Executor:** Kimi/MiMo
**Repo:** https://github.com/yujian777555/SciTransfer ; `main`
**Audited Round004 HEAD:** `304d6a49254c6dded165dfc3f8eb2267d02382a0`
**Review:** `planner/reviews/review_004.md`
**Stage:** PHASE0D / CPU_MEASUREMENT_PROTOTYPE. **This is not Phase1 strategy transfer**, not model training and not a multi-domain simulator.
**Budget:** $0 API / no GPU / no paid judge / no LLM model calls. CPU-only, bounded one-task family.
**Scientific status:** Round004 is **conditionally accepted as DESIGN**, R5 must produce falsifiable executable D1 measurement evidence. No transfer-effect claim until future independently preregistered multi-domain evaluation.

## Goal

Construct the smallest biologically/statistically plausible **batch-aware differential-expression experimental workflow** with:
1. a separately trusted hidden statistical DGP,
2. a candidate-facing stateful sequential experiment/action interface,
3. a trusted, reproducible neutral scorer using hidden treatment truth (never accessible to candidate),
4. at least one real observation→next-decision dependence in a deterministic DEV scripted policy,
5. non-degenerate scores and correct cost/FDR penalties across independent DEV instances.

This tests MEASUREMENT VALIDITY, not whether learned cross-domain strategies help. Ignore D2/D3 implementation and the selector in this round.

## G0 (MUST DO BEFORE ANY CODE) — mathematical D1 model, document and freeze

Write `research/round_005_d1_mechanism_spec.md` specifying a defensible, minimal mechanism.

Suggested starting equations (you can justify changes): for gene g, sample j:
`Y_gj ~ NegativeBinomial(mean=mu_gj, dispersion=phi_g)`,
`log mu_gj = log size_factor_j + alpha_g + beta_g treatment_j + gamma_g batch_j`.
Specify exact NB parameterization, dispersion distribution, count model overdispersion, batch/covariate assignment, normalization, treatment-effect sparsity, genuine null hypotheses and optional sample-dependence. Include at least TWO mechanism variants (unconfounded vs partially confounded; or homoscedastic vs heteroscedastic). Do NOT make batch perfectly equal treatment without a proper identifiability label; compute full-rank/overlap checks and reject unidentifiable tasks. Call out assumptions: this is synthetic expression modeling, not a validated biological mechanism or a reanalysis of GEO.

Specify:
- hidden `theta` and independent evaluation holdout, with candidate unable to infer hidden beta from seed;
- initial public task text / legal actions / per-action observations and costs;
- action types e.g. `ALLOCATE_REPLICATE`, `MEASURE_QC`, `ADD_CONTROL`, `FIT_MODEL`, `COMMIT_HITS`. Each must have **real state/measurement consequences**, typed validation, hard budget;
- explicit artifact submitted for scoring and no reward branching by strategy name/ID;
- scoring: false discovery proportion FDP = V / max(R,1), realized power = S/max(|true_alternatives|,1) with explicit all-null handling, declared FDR-control report versus realized FDP, sample cost. Distinguish expected FDR over repeated datasets from single-task FDP and avoid conflating FDR with a realized per-task statistic. Report **raw** FDP/power/cost; any scalar utility has fixed prereg weights and never substitutes raw values.
- process-causal DAG, mechanisms and testable consequence of replication/batch QC, without scripting a reward bonus for a specific action or strategy.
- consistent pseudorandom protocol: use cryptographic derivation of stable, separate secret master task seed and sample/measurement IDs for data/noise. **Avoid only one mutable RNG stream per arm**; adaptive action order and different number of calls must not accidentally alter common random conditions. When actions request different measurements, identify paired comparison limitations honestly.

Prior to implementation, **commit design spec alone as a separate Git commit**. This is a local engine-spec freeze, NOT a scored target preregistration; no scored target tasks are authorized this round.

## G1 — minimal secure engineering

Implement small, typed, modular D1 only:
- `src/scitransfer/simulator/dgp/bio_expression.py`: task generator, seed controls, latent truth; deterministic by explicit secret seed and task key;
- `src/scitransfer/simulator/engine.py`: explicit reset/step, allowed actions with input constraints and budget; public observation only; no hidden theta in memory dump, errors, returned dict or log;
- `src/scitransfer/simulator/evaluator.py`: trusted scoring in a **separate process or equivalent enforced OS isolation**, not a second class with the same candidate-accessible state/handle;
- `src/scitransfer/simulator/contracts.py` as needed for typed public events; `tests/test_d1_*.py` for real checks.
Use one local Python interpreter and free CPU dependencies; no full multi-domain infrastructure or model harness. Prefer narrow and maintainable over 2,000 LOC for its own sake.

The scorer must consume a candidate artifact and private server-held task ID -> hidden truth; candidate cannot construct an evaluator object with access to theta. If OS/process isolation not feasible, mark G1 FAIL and stop rather than claiming “secure” from variable names. Use a real loader→candidate public view nested canary test, including tool errors/logs/files (not a manually built fake candidate dict).

## G2 — actual causal process smoke, no model

Use only DEV tasks generated from frozen D1 specs. No Phase1 strategy candidate or paid LLM.
- Under fixed task/version, run >=2 reference scripted policies: naive fixed-allocation and feedback-conditioned QC/replication policy. Scripts must be blinded to hidden truth and have identical maximum legal budgets; monitor actual consumed actions/samples.
- Demonstrate at least ONE **recorded observation-dependent changed action**: perturb lawful QC or variance observation and show a different next decision, then replay to verify the changes are not due to step counter or hardcoded result.
- Score >=4 DEV task instances spanning the two frozen mechanisms, with both policies. This is a **measurement calibration smoke** only; do not report a transfer effect estimate or claim the heuristics were source learned.
- Test perfect/poor/empty discovery submissions; true nulls/all-signal cases; overlapping vs identifiable designs; invalid actions; budget exhaustion; dropout/reset; independent hidden seed replay. Score must be finite and correctly calibrated; record cases where scoring is degenerate or too easy.
- **Strategy-identity invariance:** identical action trace/artifact with altered strategy label/prompt text must yield identical evaluator score, and changing hidden mechanism should change data/outcomes. Blinded policies cannot inspect evaluator/gold.
- Signal realism: if both neutral policies always score zero/max or an arbitrary manually written policy is rewarded by design, report NO-GO. Do not retune frozen scoring weights after looking at comparative results; any necessary correction requires a new documented version and separate DEV only.

## G3 — provenance, testing and honest status

- Capture source and evaluator hashes, Python & core dependency versions, reset seeds (hashed/opaque to candidate), action-level public JSONL with true observations/actions, no hidden theta or gold.
- For each DEV task, save raw FDP, power, discovered count, false positives, samples and cost, plus properly labeled `SIMULATOR_DEV` scalar score if used.
- Run targeted pytest plus complete existing `python -m pytest tests/ -q -ra` and save actual command stdout/return code; critical security/evaluator tests cannot be silently skipped. Schema contract must be validated or distinctly versioned as simulator dev artifacts.
- Existing result schema `schemas/result_round.schema.json` requires `environment`, `runs`, `tests.skipped`, `artifacts`, and `AC-01..06`. Use the **existing schema exactly** for `results/result_round_005.json` with `runs=[]` if these DEV smokes cannot be honestly represented as official benchmark runs, and put DEV event/result arrays in a separate typed `results/round_005_d1_dev.json` file. Never set official_evaluation=true for simulated scores.
- Submit `results/round_005_measurement_audit.md` documenting biases, failure paths, score distribution and independent process proof; `results/result_round_005.json`; updated `status.json`. All JSON/MD must remain plain Git blobs; do not restore global Git LFS on them.

## R5 acceptance gates (Planner only)

- **R5-01** Frozen mathematical D1 specification and identified DAG/identifiability assumptions committed separately **before** implementation.
- **R5-02** Actual DGP and sequential real evidence/actions (two mechanism regimes), budget/invalid-action handling.
- **R5-03** Trusted evaluator isolation plus candidate loader canary & score-strategy-ID invariance.
- **R5-04** Correct raw FDP/power/cost and cases including all-null, missing answer, confounding, independent reproducibility.
- **R5-05** >=4 genuine DEV task instances ×2 blinded policies, observable evidence-conditioned action, nontrivial score variation or honest NO-GO.
- **R5-06** Actual tests, reproducible safe traces, correct result schema, commit + push; cost $0 and no Phase1/paid calls.

**Hard stop:** If DGP math, identifiability, privacy/isolation or non-degenerate evaluator cannot work without reward hacks: stop and return `BLOCKED/NO_GO`. No automatic new round, no D2/D3 yet. A D1 success only authorizes Planner review and a separate decision about whether two more mechanism families are worth implementing.
