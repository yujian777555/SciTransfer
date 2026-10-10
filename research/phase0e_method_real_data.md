# Phase 0-E — Scientific Workflow Strategy Transfer: Method v0 (DESIGN ONLY)

**Central question unchanged:** Do process-level strategies extracted exclusively from source scientific analysis tasks **causally** improve outcome-grounded target analyses, and can we abstain before negative transfer?

## 1. Minimal task formalism

A real-data task is `task=(dataset_version, science_domain, public_train_partition, public_dev_partition, private_test_partition, allowed_tools, budget, target_metric)`. No custom data-generating physics; measured labels are from pre-existing data, frozen before target evaluation. A true domain-specific public workflow:
`inspect metadata → choose QC/feature/validation/model tool → inspect public DEV measurement/model diagnostic → revise tool/config → submit final predictions and provenance`.

A candidate only sees (task statement, legal callable tool metadata, train data, allowed DEV aggregate feedback, public execution events). The trusted scorer obtains private test labels from access-controlled separate process, computes a **predefined unmodified metric** RMSE/MAE or confidence-interval coverage, and returns final score AFTER submission. During agent operation, test labels/scorer code/files are unmounted and network is restricted to deny public dataset label fetch; high contamination from pretraining or Web remains a limitation.

The benchmark's *original measured property* is real, but the task/score protocol constructed by SciTransfer is **new**, not the original dataset authors' official benchmark result.

## 2. Intervention and causal identification

Freeze dataset hashes, split IDs, permitted tool actions and base agent. For each independent target task:
- A: no strategy, same instructions/tool rights/budget;
- B: **source-extracted, frozen conditional research-process strategy**;
- C: prompt-length-matched neutral placebo;
- D: generic science/validation checklist;
- optional E: mismatched strategy (negative transfer control), F: raw source trace, G: random source strategy.
Use common task and compatible stochastic seeds, counterbalance arm order, and same model/version/config, max steps, timeouts and token or CPU budgets. If policy B requires more strategy tokens, report overhead and either match context length or account for costs; do NOT quietly grant B more context/time. Arm A score may be absent when task failed; mark FAILURE and handle under prereg rules, not prune.

All scoring is **independent of strategy ID**. Compare paired raw outcome deltas `q_B - q_A` (carefully account for lower-is-better RMSE/MAE) and separate resource costs `c_B-c_A`. Avoid previous arbitrary utility divided by cost that rewards additional spending on poor outcomes; only if justified later combine by a preregistered signed penalty `u=-normalized_error-lambda*cost` with fixed scale/lambda and sensitivity plot. Outcomes and costs always reported separately.

## 3. Source-only learning is compulsory for actual transfer claims

Do not handcraft a desirable instruction and call it learned. Acquire source-domain trajectories **using only train/DEV outcomes and public input**, include failures and contrasts. Extract preconditions, generic research action, expected observable evidence, adaptation rule, invalidity conditions, cost and source provenance. Freeze extraction algorithm and strategy file/sha before opening target scored outputs.

Possible shared strategy:
```
When a validation result changes substantially after leakage-resistant grouping,
trust the grouping-respecting split for model selection; run one diagnostic
comparison and avoid reporting random-split quality as out-of-group generalization.
```
For chemistry this means compare random vs molecular-scaffold groups; for GIS compare random vs blocked geographic stations. The strategy transfers at PROCESS level, not by calling one domain's tool in another domain. This is a methodological hypothesis, NOT proof of novelty; must challenge it against a strong standard leakage-safe pipeline and generic checklist.

Source learning may be performed later with rule induction, a small model or a fixed LLM; no learner implementation or paid model use authorized in this Phase0E design. If no source-derived strategy has useful variation beyond strong baselines, mark no-go rather than manufacturing performance.

## 4. Test-independent observations

Tools may offer QC diagnostics and DEV scores on legally exposed DEV labels; NEVER official private test score while candidate is selecting action. A real “sequential scientific decision” is demonstrable only if changing a permitted public diagnostic *at the same decision state* changes a legal subsequent analysis action, and the action changes final predictions on actual heldout labels. Merely submitting fixed models each time or printing alternative methods does not pass.

“Acquiring observations” means revealing held-out parts of a PRE-EXISTING DEV pool at explicit resource cost; it is not performing new chemical synthesis nor collecting new weather data. Any optional information-acquisition mechanism must be transparent and cannot depend on candidate strategy name.

## 5. Statistical evaluation, negative transfer, abstention

Predefine independent task units (e.g. disjoint scaffold clusters/datasets, disjoint regions/year blocks), prevent pseudo-replication from many seeds on same small dataset. Use paired task deltas and cluster/bootstrap CIs by task families / data source; reserve sufficiently many truly independent units for publication-scale conclusions. With only ESOL 1,128 compounds and one NOAA subset, report this as limited proof-of-concept: do not count arbitrary repeated splits as independent scientific domains.

Negative transfer is a paired measurable outcome degradation after real heldout evaluation, not a preassigned domain mismatch. First demonstrate a source learned strategy vs baseline effect. Only then, if enough SOURCE/DEV paired labels and variance, design a calibrated utility-difference predictor with a principled lower-bound threshold. Abstention always falls back to same A policy, with selection cost counted; never reward “abstain” for skipping scored tasks.

**Do not implement a selector or Phase1 in design round.**

## 6. Disqualifying conditions

- public data has no verifiable measured labels / acceptable license;
- dataset is already tiny, trivially solved, or label-memorized such that sealed holdout is implausible;
- task interventions are merely renaming hyperparameter loops without scientific process choices;
- weak strong baselines make prompt transfer look useful only due to unfair treatment;
- candidate can read private labels or repeatedly query the grader;
- “biology FDR ground truth” is treated as known when it is not;
- none of two domains provides multiple independent tasks and an evidential sequential workflow.

These are research-level GO/NO_GO conditions; no automatic alternative simulator launch.
