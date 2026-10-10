# SciTransfer — Planner Round 006: Real Scientific Data / Independent Scorer Feasibility DESIGN

**Issued:** 2026-10-10
**Authorization:** user approved investigating a narrower true public scientific analysis/data + independent scoring approach following `NO_GO_D1_MVP`.
**Planner:** ChatGPT | **Executor:** Kimi/MiMo
**Repo:** https://github.com/yujian777555/SciTransfer (`main`)
**Previously reviewed HEAD:** `a9cbd63578174926e92230b7d167ab4a61d10920` 
**Phase:** PHASE0E (NEW MEASUREMENT FEASIBILITY), Round006-DESIGN-ONLY.
**Hard spend limits:** **$0 paid API, no LLM calls, no GPU, no model/strategy training, no new benchmark code or target scored runs.**
**Core charter unchanged:** `planner/PROJECT_CHARTER.md`. Old D1 synthetic DEV and R5/R5R1 NO-GO preserved byte-for-byte.

## STOP trying to repair old simulator

Do not modify or expand `src/scitransfer/simulator/`, D2/D3, DiscoveryWorld or SciAgentGym. The R5-R1 hard stop was on the current synthetic D1 implementation. This new plan is a **separate, user-approved METHOD FEASIBILITY inquiry**, not “R5-R2”.

Read `status.json`, `planner/latest_plan.md`, `research/phase0e_real_data_candidate_audit.md`, `research/phase0e_method_real_data.md`, `research/phase0e_novelty_feasibility.md`, `planner/reviews/review_005_r1.md`.

## Workstream A — evidence audit of REAL labels and executable tools

Examine original sources and actual acquisition paths for:
1. **Priority CHEM:** DeepChem Delaney/ESOL (~1128 SMILES + experimental solubility values), scaffold split, RDKit/safe lightweight sklearn baselines. Verify original data rights separately from code license, exact file/version and whether fixed target split can remain private to candidate.
2. **Priority SPATIAL:** NOAA GHCN-Daily **restricted to small bounded station region/year**, inspect measurement/Q/S flags, time/station duplicate risks, ability to form blocked holdout. NEVER download multi-GB GHCN archive; only inspect docs/HEAD/metadata, no bulk materialization.
3. **Optional BIO:** Bioconductor airway/pasilla and DESeq2 mature R pipeline, BUT no exhaustive true DE gene list. Only propose an independently defensible target metric / true spike-in or replication truth, or reject BIO from outcome-grounded gate. Do not invent realized FDR as gold.

Create `research/round_006_data_source_audit.md` including dataset URL/DOI, author/release/source hash candidate, data license and redistribution uncertainty, file/metadata size, sample count, split schema, real measured labels, missing data/quality flags, scorer definition, expected offline environment, CPU/RAM/network/setup risks. Use explicit VERIFIED_DOC / BLOCKED / UNCERTAIN. **No bulk data download.** Read-only, minimal HTTP HEAD checks acceptable, but no writing code, installing packages, executing models or evaluating real target scores this round.

## Workstream B — real analysis *sequential* decision contract

In `research/round_006_workflow_contract.md`, define actual action grammar for ESOL (chemical standardization, descriptor QC, scaffold grouping, fit regressor, inspect allowed DEV residual, revise) and NOAA (quality filter, station/time blocking, interpolation model, inspect only DEV residual, revise). Each action must be a real analysis on public data, results reproducible by a pinned existing scientific library. Need single legal observation difference→different next action without revealing test labels or calling target grader. Explain no new chemical reaction or weather observation is physically generated. Propose a shared **source-extracted** conditional process strategy with explicit preconditions/expected evidence/adaptation/failure; compare to well-designed domain-specific standard pipelines, NOT weak strawman.

Separate candidate runtime and trusted scorer by OS/data access and blocked network. Actual proposed target set/metric fixed by independent actor before agent calls. Define prevent labels known to base LLM contamination and count residual limitations.

## Workstream C — causal and falsifiable evaluation

In `research/round_006_experiment_identification.md`: formal target estimand (paired held-out RMSE/MAE improvement as correct sign), unit independence (molecular scaffolds vs region/time station blocks), frozen splits, same models/steps/token budget, control A baseline, B source learned strategy, placebo C, strong domain-default D, random E, cost/time secondary. Negative transfer vs abstention only if labels allow; define fail/partial outputs and cost tracking. **Do not fit predictor or claim cross-domain gains.**

Make a specific proposal for how many independent real task units are plausibly obtainable from ESOL and NOAA and why repeated random seeds/other splits are not independent; mark exact n as TBD from catalog. Design an external-validity layer beyond simple train/test score if feasible, and stop criteria if data too small, labels too public/contaminated, strategies reduce to standard CV hygiene.

## Workstream D — novelty and research value independent review

Write `research/round_006_novelty_and_risk.md` evaluating SciAgentGym/SciForge, Memory Transfer Learning, MCMA, Co-Scientist, Robin, AI Scientist, PrimeScientist, Metacognitive Steering, COGTRL, EvoScientist, MARS and closest selective prediction/calibration papers where verified. Cite primary URLs and distinguish VERIFIED vs UNVERIFIED. Construct a table with exact novelty collision, required extra experiment for a narrow technical contribution, and whether a scientifically honest **CCF-B-level** paper is plausible *conditioned on evidence*, not a submission promise. If no genuine new method is defensible, mark NO-GO rather than code a generic pipeline.

## Workstream E — skeptical research decision and cost

Write `research/round_006_feasibility_decision.md`: make strongest negative case against strategy transfer here, including public-label contamination, only 2 domains, ordinary CV advice collision, noisy small metrics, license/CPU costs. Six gate statuses E1..E6 with evidence/links and GO (only for later micro-smoke), CONDITIONAL, NO-GO. Provide a **single smallest future CPU-only micro-smoke** if evidence warrants it: ESOL dataset and bounded NOAA sample loading, baseline outcome verifier and hidden scorer smoke only, not learned strategy/no LLM; its execution requires a NEW Planner authorization after Round006.

Deliver `results/result_round_006_feasibility.json` conforming to `schemas/result_round.schema.json` EXACTLY: no unknown top-level keys; `round=6`, `runs=[]`, `environment.official_evaluator_verified=false`, `environment.benchmark` describes *proposed* real task protocol, `AC-01..06` present, `tests` truthful (design-only => counts=0). Put arbitrary E1..E6 gate detail inside separately linked Markdown, not the strict JSON's acceptance map.
Update `status.json` to `AWAITING_PLANNER_REVIEW`, keep plain Git files readable; commit/push main and hand off full SHA. **Do not claim data installed, tested, accessed or downloaded unless command evidence exists.**

## R6 feasibility gates — Planner-only acceptance

- E1: source-authoritative datasets/versions + legal and data acquisition feasible (not just claimed).
- E2: actual independent measured labels and valid frozen holdout, accounting for contamination and leakage.
- E3: task-specific scientific decisions beyond general ML hyperparam tuning, truly meaningful feedback and strong baselines.
- E4: causal matched intervention and source-only strategy acquisition, uncertainty and negative transfer are testable.
- E5: defensible narrow novelty with close-paper collision matrix and explicit nonnovel alternatives.
- E6: executable tooling, CPU data/rights budget and stop criterion plausible; no experiments/code in R6.

**HARD STOP** if no two independently scoreable real tasks, no scientific transfer construct beyond a checklist, or no way to prevent candidate access to test labels. Do NOT start Round007, Phase1, multi-domain code, paid models or another invented simulator. Let Planner and user decide after reviewing evidence.
