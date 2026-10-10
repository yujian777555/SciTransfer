# SciTransfer — Planner Final Scientific Audit: Round 005-R1

**Audit date:** 2026-10-10
**Audited implementation commit:** `576b21380d9ab30c8aa7aa5262cab5311bd45210` (GitHub main at audit start).
**Verdict:** **NO_GO_D1_MVP** — engineering partial; hard scientific measurement gates R5R1-02, -03 and -05 NOT MET.
**Mandatory stop:** No more autonomous R5-R2/R5-R3 remediation. No D2/D3, Phase1 strategy training, paid LLM, GPU, target trials or transfer claims. Await user's explicit decision about revised research feasibility.

## Provenance and positive evidence

Read `research/round_005_r1_d1_corrective_spec.md`, `src/scitransfer/simulator/dgp/bio_expression.py`, `src/scitransfer/simulator/engine.py`, `src/scitransfer/simulator/evaluator.py`, `tests/test_d1_r1_integrity.py`, `scripts/r5r1_dev_smoke.py`, `results/round_005_r1_dev.json`, `results/result_round_005_r1.json`, `status.json` from actual GitHub. No local pytest or Windows runtime independently executed by Planner; reported 133/133 is an Executor claim without committed complete stdout/exit transcript. The following findings are directly reproducible by inspecting committed code.

1. Separate **corrective mathematical spec freeze** `49621591dc3df58ed43e2c049ab4fbce1b74799b` precedes implementation `576b21380d9ab30c8aa7aa5262cab5311bd45210`. Valid G0 engineering provenance; not a prospective target preregistration.
2. Gamma–Poisson count DGP now sets M1 `phi=np.full(G,config.phi0)` and M2 gamma-distributed `phi`, resolving one prior mismatch. Treatment is randomized within each batch with a design-rank/within-batch-overlap check for common valid configs.
3. `Action` no longer has a public cost field; costs are computed server-side in `engine.py`. `MEASURE_QC` now reveals only requested gene statistics and `FIT_MODEL` computes SciPy two-sample t-statistics/p-values for *previously measured* genes.
4. `score_submission()` deduplicates inputs and computes realized FDP/power for valid sets. Blank submission utility is zero for non-null tasks. Four task IDs × two manually scripted policies yield a spread of raw FDP/Power; this is a limited **DEV diagnostic**, not valid scientific policy improvement.

## HARD FAIL R5R1-02: No actual newly acquired experiment data

`engine.py::step` handles `ALLOCATE_REPLICATE` by incrementing `self._allocated[group]` and making an `info={'added':n,'group':group}` dict. It **NEVER appends new columns to `self._Y_current`**, never updates `self._truth.treatment`, `self._truth.batch`, size factors or sample IDs, never derives sample-specific RNG and never changes the measurements. The code comment explicitly says “In simulation, we just track counts; Y already has all samples.” Meanwhile `_get_observation()` group sizes are computed from immutable `self._truth.treatment`, not `self._allocated`; its `qc_summary` is computed from immutable `Y_current`. Candidate `get_public_view()` instead shows extra allocated counts, an inconsistent view. `MEASURE_QC` reveals existing pre-generated values; repeated measures are cached. `FIT_MODEL` computes on the same original samples. Only information reveal changes; **repeated experiment allocation is inert and scientifically false**. Tests `test_a2_allocate_changes_state` check counter and info only, not count matrix, group sizes, or independent observation differences.

Other validation issues: bool is an `int` in Python, so bool-valued replicate counts or gene IDs pass `isinstance(..., int)` checks; `_server_cost` uses floor `len(gene_subset)//10` rather than a documented ceiling per 10 genes; duplicate QC genes may reduce information per cost; resource guards use `sum(_allocated)+n` and omit the initial N samples. Unknown mechanism values fall into M2 rather than rejection. Not all parameter boundaries are covered.

## HARD FAIL R5R1-03: No trusted candidate/grader boundary

The candidate-visible Python `ExperimentEngine` retains `self._truth` and `self._master_seed`; `scripts/r5r1_dev_smoke.py` directly calls `score_submission(engine.submitted_genes,engine._truth.true_non_null,engine.total_cost)`. `src/scitransfer/simulator/evaluator.py` is a pure function in the SAME process; no separate process, allowlisted IPC protocol, filesystem sandbox or adversarial hidden-field loader is in commit. `test_a6_no_hidden_truth_in_public_view` merely verifies that a string rendering of `get_public_view()` omits some words; nothing tests candidate import/path access, malicious action data, stack traces or nested canary transit. The submitted report openly acknowledges “Function-level isolation (not OS process isolation).” This is insufficient by the stated hard R5R1-03 gate.

## HARD FAIL R5R1-05: No demonstrated scientific feedback/counterfactual

In `scripts/r5r1_dev_smoke.py`, `naive_policy(engine,step)` and `feedback_policy(engine,step)` branch on step index, NOT on any observation statistics. Feedback executes fixed replicate actions and different `gene_subset`/submission cardinalities. It reads `engine._measured_genes` private internals rather than the public candidate observation contract. `test_a3_observation_changes_next_action()` constructs DIFFERENT task keys, measures different gene sets, and finally asserts only `action1.action_type != ''`; it does NOT assert `action1 != action2` and does not hold state/budget/tool set fixed. Hence the test would pass regardless of true evidence influence. The 8 DEV FDPs 0.60–1.00 and powers 0–0.16 vary mainly with task and submitted gene-list choice. Nothing establishes a within-task effect of an actual measurement or scientific adaptation. No source-derived/target strategy tested.

## Additional statistical/scoring failures

- `FIT_MODEL` uses plain independent Welch? actual call `stats.ttest_ind(treat, ctrl)` with default equal variance; no batch regression/NB GLM, no multiplicity adjustment or Benjamini–Hochberg and no control of the *expected* false discovery rate. Reporting realized FDP/power is permissible; claiming "FDR controlled" or a scientifically verified discovery procedure is not.
- Both mechanisms randomize treatment within batch to approximately half, so M2 has nonzero *batch effects* but the claimed **partially confounded treatment allocation** is not implemented. Within-batch randomization can make treatment independent of batch by design; mechanism narratives must distinguish nuisance batch heterogeneity from true confounding.
- `score_submission` performs no validation of out-of-range or noninteger IDs if called directly; the engine validates at `COMMIT_HITS` but uses `isinstance(g,int)`, accepting booleans; private score entry point accepts arbitrary caller truth and cost. All-null `utility=0` even if false discoveries are reported, so scoring fails to penalize scientifically false claims on all-null tasks.
- Proposed “regret” utility `(power-fdp)/max(sample_cost,1)` is NOT conventional oracle regret and has a serious sign reversal: when numerator is negative, increasing sample cost produces numerically **higher** utility (closer to 0). All 8 committed DEV utilities are negative. In the results, naive vs feedback uses cost=7 vs 11; e.g. task `dev_m1_b` both FDP=1 power=0 but naive -1/7 and feedback -1/11, meaning **6 extra? actually 4 extra cost receives a better score for identical scientific output**. The scorer should avoid this perverse incentive; do not retune based on which strategy “wins.” Labels like “neutral” or “regret-based” are unsupported.
- Data generation remains a highly simplified independent-gene NB model, not real bioinformatics experimental findings. M1/M2 independence of scientific method cannot be assessed from this alone.

## Result and tests remain noncompliant

`results/result_round_005_r1.json` has valid JSON and uses `AC-01..06`, but `schemas/result_round.schema.json` sets `additionalProperties:false`. Extra fields `round_label`, `runs_note`, `dev_results`, `acceptance_detail`, `decision`, `decision_rationale` make validation fail. `official_evaluator_verified:true` is misleading if interpreted as upstream/official scientific benchmarking: this is only a custom simulator pure function; distinguish internal DEV scorer verified versus externally official benchmark. Missing genuine `runs` is honestly [] because no official benchmark episode was run; retain that.

Original 133-passed full-suite test output/exit code is not committed for independent inspection. Most critically, security and counterfactual tests contain false-positive assertions and the code's intended scientific invariants are not covered. **Even if 133 tests genuinely pass, they do not establish the stated gates.**

## Formal gate disposition

| Gate | Planner verdict | Reason |
|---|---|---|
| R5R1-01 | PASS | Corrective spec isolated in an independent preceding Git commit |
| R5R1-02 | FAIL | Allocation increments counter only, no new scientific samples, group sizes unchanged |
| R5R1-03 | FAIL | Hidden truth & private seed accessible in-process, no adversarial loader canary/OS boundary |
| R5R1-04 | PARTIAL | Basic FDP/power/set arithmetic; nonneutral utility sign inversion, all-null and validation issues |
| R5R1-05 | FAIL | Scripts are step-based, tests do not prove counterfactual action changes |
| R5R1-06 | PARTIAL | 133 green Executor-reported, schema invalid, key negative tests inadequate |

## Final Planner decision

**NO_GO_D1_MVP — final authorized R5-R1 repair gate closed without measurement acceptance.** Preserve original R5 and R5-R1 data and code as engineering exploration, do not rewrite timestamps or invent missing logs. No R5-R2/R6 code plan automatically issued. Keep `status.json.state=BLOCKED` until user approves one of:

(A) Park SciTransfer's proposed simulator-first research to avoid further sunk cost;
(B) Scientific redesign with a narrower valid, existing-statistical-package executable experiment as anchor (real differential-expression workflow, external independent scorer; source→target transfer research question retained), requiring user consent, costs/licensing and preregistration;
(C) Bring an externally verified scientific research task runner/evaluator, then Planner reconsider once.

The preceding recurring implementation-instead-of-measurement pattern is a serious feasibility warning; a new design must include independent end-to-end causal science validation BEFORE any cross-domain expansion or learned selector. **Phase1, D2/D3, LLM experiments and paid APIs remain unauthorized.**
