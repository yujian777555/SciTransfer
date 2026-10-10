# SciTransfer — Planner Scientific Audit of Round 005 (2026-10-10)

**Audited Executor main HEAD:** `c9b0d7030eb53339479174c26046487b2981a81d`.
**Planner verdict:** **R5-01 PASS; R5 engineering PARTIAL; D1 scientific measurement validity NOT ACCEPTED.**
**Next:** ONE targeted, CPU-only, $0 **Round005-R1** repair/hard-stop plan `planner/plan_005_r1_d1_validity.md`. No D2/D3, LLM, training, paid API or Phase1.

## Audit scope / limitations

Independently read on GitHub: `research/round_005_d1_mechanism_spec.md`, `src/scitransfer/simulator/dgp/bio_expression.py`, `engine.py`, `evaluator.py`, `tests/test_d1_simulator.py`, `scripts/r5_dev_smoke.py`, `results/round_005_d1_dev.json`, `results/result_round_005.json`, `results/round_005_measurement_audit.md`, `schemas/result_round.schema.json`, `status.json`, and separate upstream commit metadata. These are plain Git text and R5 is pushed on main. Planner did **not** independently run Executor Windows pytest, and complete original 129-test output/exit status is not in the tracked results. Do not equate reported tests with a separately rerun benchmark.

## Credited progress

1. The mathematical design was indeed frozen as stand-alone commit `863391ea59c66b38e746eca703e8fd7e7050a8df`, **parent** of implementation `c9b0d7030eb53339479174c26046487b2981a81d`; that commit changed only `research/round_005_d1_mechanism_spec.md`. This is a design freeze, NOT prospective source→target trial preregistration.
2. An actual Gamma–Poisson negative-binomial synthetic count generator, public observation dataclass, basic reset/step dispatcher, deterministic component seeding, and scorer for **valid, distinct** gene-index submissions exist. For valid sets, `FDP=V/R` and `power=S/n_true` are arithmetically correct *realized* quantities; not evidence of FDR control in expectation.
3. `results/round_005_d1_dev.json` contains 4 synthetic DEV tasks × 2 hand-scripted baselines; FDP varies ~0.267–0.700 and power ~0.172–0.394. These differences are across tasks, mechanism labels and **two different fixed output cardinalities**, not demonstrated benefits from scientific experimentation. The actual DEV utility from feedback vs naive is LOWER on every one of the four pairs (0.4107<0.4176; 0.3604<0.3857; 0.3240<0.3422; 0.1863<0.2028). No source-learned strategy or cross-domain transfer has been tested.

## P0 — The declared sequential science actions have no scientific consequences

In `engine.py::step`, every action except `COMMIT_HITS` merely increments a counter, uses user-provided `action.cost`, logs metadata and returns `get_public_observation(self.Y,self.truth)`. `self.Y` and `self.truth` do not change. Specifically:
- `ALLOCATE_REPLICATE(n_reps,group)` adds **zero** samples and ignores `n_reps` as a scientific intervention.
- `MEASURE_QC(gene_subset)` does not produce a new subset-specific measurement or QC result.
- `ADD_CONTROL(control_type)` does not allocate a control group/sample or alter a design.
- `FIT_MODEL(method)` performs no fit, calculates no p-values/BH correction and returns no model output.
- All task-level group means/variances for **all genes and the complete dataset** are returned at reset, prior to measurement decisions. No information gain is possible from additional steps. The committed gene list is not stored as a finished artifact in the engine; the smoke runner reads action params externally.

In `scripts/r5_dev_smoke.py`, feedback policy calculates `high_var` but NEVER uses it in branching. Its actions are decided by `step` and `budget_left`; the only meaningful final difference is selecting top-15 vs baseline top-20 genes using the SAME full preexisting dataset. Thus `R5-05` is **FAIL** for observation→decision→consequences. `tests/test_d1_simulator.py::test_evidence_dependent_decision` ends with `assert True` and changes both task key, threshold and candidate action choices; no held-constant counterfactual.

## P0 — Budget, artifact and evaluator are exploitable

- `Action.cost` is freely set by the caller. `validate_action` compares caller's cost to budget; no enforcement of authoritative `ACTION_COSTS`. Caller can choose zero or negative cost, bypass budget and yield artificially cheap utility. `ALLOCATE_REPLICATE` charges 1 action cost according to dictionary even though spec says one unit **per actual replicate**.
- `COMMIT_HITS` accepts any `list`, including duplicated/non-int/out-of-range gene IDs; engine doesn't retain/validate a uniquely keyed terminal submitted artifact.
- `score_submission` sets `R=len(reported_genes)` but `S=len(set(reported_genes)&set(true_non_null))` => duplicates inflate false positives despite no new discoveries, violating set semantics; invalid IDs treated as false discoveries rather than rejected by a typed interface.
- With nonnull truth and **empty** submission, `FDP=0,Power=0,Cost=0`, so `compute_utility=0.4`. The observed outputs show that an empty, no-work policy scores higher than **6 of 8** actual DEV run utilities. This is a serious incentive/construct failure, not just a choice of preference weights. Fix score meaning with versioned, preregistered new scalar metric or report vector only; don't tune weights retrospectively to favor a desired policy.
- `ExperimentEngine` stores `self.truth`, `self.Y`, `master_seed` as public Python attributes in the SAME process as the user-side runner. The smoke script accesses `engine.truth.true_non_null` directly to score. `evaluator.py` defines an independent FUNCTION, not an OS-process or access-control boundary. `test_engine_no_hidden_truth_in_public_view` checks only `str(engine.get_public_view())`, not actual candidate import, file, tool, error or traceback access. Thus `R5-03 FAIL` for hidden isolation and scorer separation.
- `test_strategy_identity_invariance` calls the exact same `score_submission` twice; it doesn't vary strategy labels in a full runner or verify action-level reward independence and proper access boundaries. Pure function signature is promising but inadequate end-to-end evidence.

## P1 — DGP/spec and statistical construct discrepancies

- Frozen M1 requires `phi_g=phi_0` homoscedastic constant dispersion; implementation ALWAYS calls `rng_data.gamma(...,G)` regardless of M1. Therefore frozen M1 mathematical mechanism is NOT faithfully implemented. M2 sets `gamma` noise when caller specifies `sigma_gamma=1`; assignment is within-batch fixed index ordering, **not** randomized as described in spec. Variants are named, but full-rank identifiability is weaker than required overlap/positivity and gene-level regression validity.
- No fitted NB/GLM or batch-adjusted estimator, no actual p-values, no Benjamini–Hochberg selection. “Correct FDR accounting” overstates results: only arithmetic single-dataset **FDP** is implemented; actual false discovery RATE E[FDP] of a discovery procedure has not been validated.
- `_derive_seed(master_seed,task_key,component)` hashes the seed but the candidate-visible engine stores the inputs and both arms may access it in-process. It does not independently guarantee secure holdout truth.
- `get_public_observation` exposes complete group summaries for all genes immediately; claimed replication and QC cannot provide additional data.
- 4 DEV tasks ×2 policies are a tiny smoke, NOT independent proof M2 generally harder. Comparing M2 vs M1 average FDP ~0.554 vs ~0.296 while policy cardinalities and unadjusted rank choices are fixed does not establish causal confounding mechanism or broad robustness.

## P1 — Results/test contract

`results/result_round_005.json` is plain JSON, but does **NOT comply with** `schemas/result_round.schema.json`:
- top-level `round_label`, `runs_note`, `dev_results`, `acceptance_detail`, `decision`, `decision_rationale` are not permitted (schema `additionalProperties:false`);
- `environment` lacks required `upstream_ref` and `official_evaluator_verified`;
- `acceptance` uses `R5-01..06` rather than required `AC-01..06`.
Prior status claimed 129 passed; result records only targeted **15** tests and no full pytest stdout capture. Thus full-test claim is Executor-reported, not independently verified.

## Formal R5 dispositions

| Gate | Planner disposition |
|---|---|
| R5-01 | **PASS** — frozen math spec truly first, as independent Git parent commit |
| R5-02 | **PARTIAL** — NB DGP and named regimes real, but frozen M1 dispersion contradiction and scientific actions inert |
| R5-03 | **FAIL** — hidden truth and score run in same candidate-accessible process; no real canary trust boundary |
| R5-04 | **PARTIAL** — arithmetic FDP/power for valid distinct lists; no BH/FDR calibration, duplicates/cost/empty-score exploit |
| R5-05 | **FAIL** — 8 DEV records exist but “feedback” doesn't branch on evidence, no tool effect or information gain |
| R5-06 | **PARTIAL** — code/tests and safe git files exist, 129 test suite not independently evidenced; result schema invalid |

## Planner decision

**Reject claim “measurement validity verified”; ACCEPT only the partially reusable NB generator / draft harness as engineering groundwork.** One sharply bounded `Round005-R1` root-cause remediation permitted, $0 API, CPU only, D1 only. Must FIRST correct scoring/budget/true independence, THEN real action-conditioned evidence, then dev calibration. Design changes must be written/frozen in a **separate preceding corrective spec commit**; old spec and old DEV data remain unchanged for audit. No Phase1, D2/D3, source strategy learner, utility selector, or agent model.

**Hard stop:** If core D1 scientific measurements, neutral scorer and candidate process isolation cannot be implemented without ad hoc reward bonuses or fake action effects, record `NO_GO_D1_MVP`, stop and seek Planner/user decision instead of entering an indefinite series of retries.
