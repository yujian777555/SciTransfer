# SciTransfer Planner Round 002 — Phase 0-B: Benchmark Suitability & Multi-Step Research Decision Feasibility

**Issued:** 2026-10-09  
**Planner:** ChatGPT  
**Executor:** Kimi / MiMo (declare actual runtime)  
**Repo:** https://github.com/yujian777555/SciTransfer  
**Branch:** main  
**Base reviewed:** `e7b5792199688f55e58453315a42ecffdc3b9c09`  
**Formal review:** `planner/reviews/review_001_r3.md`  
**State:** ISSUED / AWAITING_EXECUTOR  
**Phase:** PHASE0-B, not Phase 1 training

## Mission

Identify the smallest **runnable, replayable, affordable, action-rich scientific research setting** that could genuinely test whether an agent can transfer a research decision rule learned from one scientific task/domain to another. Build a minimal honest evidence pipeline. Avoid getting stuck in another endless benchmark repair loop.

Prior Round 001 infrastructure may be reused where sound. Round 001 remains PARTIAL/INCONCLUSIVE and is frozen as a pilot; its 0/0/timeout results cannot support strategy-transfer efficacy conclusions.

### Hard scientific construct

We are NOT measuring whether a generic extra prompt helps single-shot code generation. We want controlled, **multi-step** scientific actions that respond to observations: inspect evidence, replicate/check, design or select an experiment, analyze/falsify, revise/pivot, and stop/abstain. Domain-specific task execution tools are environment actions; strategy is a condition-to-action rule, not a task answer.

The future causal contrast must intervene on strategy availability/selection, keeping initial state, candidate tools, base model, wall/token budget and outcome verifier aligned. Historical traces alone are NOT causal labels. **Do not infer cross-domain transfer from this feasibility round.**

## Track 0 — Freeze original evidence + accurate erratum (before new experiments)

1. `git pull --ff-only`, inspect status/plan/review/HEAD/worktree. Preserve all prior files under results/round_001_*/ and original config, including known flawed outputs. No overwrites, backdating, or fabricated runtime details.
2. Create `results/round_001_r3_erratum.md` as an ADDITIVE note: core 300s timeout vs `r3_finalize.py` hardcoded 601.3s, CSV 8 data rows vs JSON 6, Task85 scorer exceptions coerced to SUCCESS/0, #16 two empty outputs, #21 null, shared full Benchmark junction exposing gold. Link exact code paths and separate direct observations from inferences. State **not independently validated** for local ZIP and unit tests.
3. Do NOT re-run Task21 with longer timeouts or edit R3 results as a condition for moving forward. The evidence integrity flaw remains documented, not repaired by retroactively changing numbers.

## Track 1 — Benchmark suitability audit (small, bounded)

Compare **at least two realistic candidates** for scientific decision research, including:
- DiscoveryWorld: controlled interactive science tasks; distinct themes are NOT automatically distinct scientific disciplines.
- ScienceAgentBench: existing four scientific domains and output verifiers, BUT mostly single-shot generated code and current selected tasks have floor/timeouts.
- Optional: SciAgentGym or other public resettable scientific environment ONLY after actual install/license/tool+evaluator readiness is confirmed.

Construct `benchmarks/suitability_matrix_round_002.md` with **observed vs inferred** columns: repo/commit/license; offline run & reset; scored reward and grader provenance; action/observation loop; at least 3 genuinely distinct disciplinary task families or a defensible plan for across-domain held-out generalization; low/no leakage; reproducibility; runtimes/space/API costs; domain and instance independence; failure and negative-transfer measurability. Explicitly reject environments that merely provide tool-use or text-only benchmarks without actual research decisions.

No more 1.7GB redownload. Timebox upstream installation attempts; record exact blocker and stop rather than patching endlessly. No raw protected benchmark upload.

## Track 2 — Minimum multi-step agent experiment, not heavyweight architecture

For most suitable **one candidate environment only**, implement a small adapter with:
- `ResearchState`, allowed action, observation/evidence, terminal outcome/reward, environment seed/reset/version and cost fields;
- a real **observe → choose action → execute → receive evidence → choose again** loop with at least two meaningful state-contingent decisions per episode when supported;
- hard time/step/token limits, immutable logs, separate candidate-facing permitted inputs and evaluator-only hidden answers (no junction to full gold tree).
- `NO_STRATEGY`, `FIXED_CONDITIONAL_STRATEGY`, and optional length-matched PLACEBO arms. Same accessible actions/tools and budget for all arms.

For this round, strategies must be explicitly labeled **hand-authored feasibility interventions**. They are NOT 'transferred/learned' and no cross-domain performance claim is allowed.

A plan or process flow alone is insufficient: show that the agent's second decision can change based on evidence from the first. No unverified offline stub counted as success.

## Track 3 — Tiny **calibration** run to avoid floor/ceiling traps

1. Before task execution, freeze a seed/task candidate set and a baseline agent/model ID. Target a **bounded sample of roughly 6–10** evaluation episodes total or fewer if environment costly. At least TWO distinct task families; assess feasibility of a third independent scientific domain. This is NOT a powered efficacy study.
2. Record each task's outcome with real evaluator, step-wise evidence, observed intermediate decisions, elapsed time, tokens and actual/specified costs. Determine if outcome scores show ANY nontrivial gradation or both successes/failures rather than uniform zero, and whether strategy intervention can physically change later actions. No assumption of positive effect.
3. If baseline uniformly fails or always succeeds, reject environment/task subset for immediate causal strategy utility modeling or redesign the task difficulty **prospectively**, not after looking at intervention outcomes.
4. Do not mix incomparable ScienceAgentBench/DiscoveryWorld raw score values into a single transfer matrix.
5. No substantial paid API/GPU sweeps; limit API spend to a modest documented ceiling of USD 1 unless the user explicitly approves more. Run offline feasibility tests first. If model/API access is unavailable, report BLOCKED; do not substitute synthetic scores.

## Track 4 — Research decision report and stop rule

Produce `results/round_002_benchmark_decision.md` answering: which environment is actually runnable/replayable? Does it contain distinct scientific task families? Is the multi-step evidence-action loop real? Does evaluation have integrity? Are outcomes nontrivial? Can future study acquire source-domain trajectories and transfer conditional policies across held-out targets? What is estimated compute and task count for a powered study?

Explicit **GO / CONDITIONAL / NO-GO** recommendation, alternatives, limitations and next minimal experiment. Planner alone decides acceptance and authorizes Phase 1.

### Must-have deliverables

- `results/round_001_r3_erratum.md` (additive; no historical rewrites).
- `benchmarks/suitability_matrix_round_002.md` and pinned candidate manifest/config.
- Minimal benchmark adapter and real multi-step decision runner under `src/`; targeted tests.
- `results/round_002_calibration/` with raw per-episode traces and scorer provenance, where feasible.
- `results/round_002_benchmark_decision.md`.
- `results/result_round_002.json` with state, tasks, completed episodes, evaluation provenance, costs, tests pass/fail/skip, blockers and acceptance gates.
- Updated `status.json`, commit and push main.

### Planner acceptance gates

- **R2B-01:** Erratum documents R3's fixed timeout data, exception-imputed 0 scores, and 8 CSV vs 6 JSON discrepancy without modifying history.
- **R2B-02:** Two candidate benchmarks evaluated using grounded executable feasibility evidence, not marketing alone.
- **R2B-03:** ONE real resettable scientific environment runs end-to-end with authentic evaluator.
- **R2B-04:** At least two genuine evidence-dependent decision steps per real episode and enforced tool/gold boundary.
- **R2B-05:** Bounded calibration traces show variation potential or explicitly demonstrate unusable floor/ceiling; no fabricated scores.
- **R2B-06:** Recorded hashes, budgets, task seeds, costs, frozen intervention, strong leakage and replay tests; honest errors.
- **R2B-07:** Clear GO/NO-GO research recommendation on **domain transfer feasibility**, no conflation of themes with independent scientific disciplines or learned policy with hand-authored prompting.
- **R2B-08:** Artifacts/status committed to main, Planner review awaited. No self-ACCEPTED.

## Stop conditions and next action

Stop immediately when: environment not legally accessible, no actual evaluator, gold cannot be isolated, an unaffordable installation, unstable resets, or no legitimate multi-step decisions. Report truthful BLOCKED, with one smallest remedial action or alternative candidate. Do not run another general build marathon. If no environment passes R2B-03/04, Planner will revise the *research method*, not pretend benchmark success.

**Theoretical promise is NOT experimental evidence. No Phase1 predictor/controller training in Round 002.**
