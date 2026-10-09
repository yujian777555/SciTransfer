# Planner Review — Round 002 / Phase 0-B (2026-10-09)

**Executor revision reviewed:** `33d51a095fa9fc98ea3fcbec3669fbc96c99a747`  
**Planner verdict:** **NOT ACCEPTED for evidence-conditioned scientific strategy evaluation; partial PASS for DiscoveryWorld environment bring-up.**  
**Decision:** **PHASE 1 TRAINING NOT AUTHORIZED.** Issue scoped Round 002-R1 to correct the **action protocol**, prove *observation-dependent* decisions, and isolate hidden evaluation content before any LLM spending.

## Sources and verification level

Examined the actual GitHub main files: `src/scitransfer/discoveryworld_adapter.py`, `scripts/r2b_calibration.py`, `tests/test_r2b_adapter.py`, `results/result_round_002.json`, two Reactor Lab traces, and suitability/decision documents. Checked official `allenai/discoveryworld` `DiscoveryWorldAPI.py` and `ActionHistory.py` interfaces (live main; pin a source commit in the next round). Confirmed real GitHub repository `CMarsRover/SciAgentGYM` is public. Planner did **not** independently rerun DiscoveryWorld or the Executor-reported `82 passed`.

## Credible accomplishments

- DiscoveryWorld environment was installed and called by a Python runner; 12 episode files for four named science-themed scenarios, two arms and seeds 42/43 as documented. `loadScenario`, `getAgentObservation`, `performAgentAction`, `tick`, and `getTaskScorecard` are all present in source.
- Scorecard is taken from the actual benchmark API rather than hallucinated. Rules and source labels are explicitly `hand-authored feasibility`, not learned transfer. API cost is $0 as reported.
- `results/round_001_r3_erratum.md` exists (check for completeness in subsequent targeted review if needed).
- No Phase 1 model training or cross-domain causal effect was claimed.

## Critical flaws invalidating the apparent multi-step decision claim

### P0 — INVALID DISCOVERYWORLD ACTION SCHEMA

Current `SimplePolicyAgent.decide` emits:
- `{"action":"moveAgentForward"}`
- `{"action":"pickupObject","objectName":"key"}`
- `{"action":"useObject","objectName":"jar"}` or `chemicalDispenser`.

Actual upstream `ActionHistory.ActionType` and `DiscoveryWorldAPI.additionalActionDescriptionString()` specify action names including **`MOVE_DIRECTION`, `PICKUP`, `USE`**, with `arg1`/`arg2` and UUID/direction as applicable. `DiscoveryWorldAPI.performAgentAction` returns `errors` and `success`; the adapter does not assert or aggregate success. Therefore there is **no demonstrated count of valid scientific actions** in the 12 episodes. World ticking may proceed even when action parsing fails. First fix the action syntax and prove accepted actions with actual returned success fields.

### P0 — NO OBSERVATION-CONDITIONED DECISION POLICY

`SimplePolicyAgent.decide(observation, task_description)` **does not inspect either argument** to pick an action. It branches solely on `self.action_count` (steps 1–3 move, 4–6 pick up hardcoded key, 7+ use hardcoded object); strategy branch changes actions after count>5, not due to measured task progress. `is_decision_point = action_count >= 2` is an arbitrary label and `n_decision_points=14` provides **no evidence of observational adaptation**. Two observations with the same action count produce identical decisions; any claim of evidence-conditioned scientific research is unsupported.

### P0 — NO REPLAYABLE STEP-BY-STEP TRACE

`EpisodeTrace.to_dict` returns `n_observations=len(self.observations)` and `n_actions=len(self.actions)`, but the completed `run_episode()` does not pass observations or actions into the dataclass, only `scorecard`. All examined episode JSON entries show `n_observations=0` and `n_actions=0`, despite `steps_taken=15`. `agent.history` captures truncated strings internally but is not returned. This violates the 'immutable evidence trace' requirement; scores alone cannot prove actual decisions.

### P0 — HIDDEN EVALUATOR INFORMATION STORED AND ACCESS CONTROL NOT PROVEN

`run_episode` obtains `getTaskScorecard()` **before** acting, extracts `taskDescription`, and saves an unfiltered final scorecard. Committed Reactor Lab episode contains `criticalHypotheses` and `criticalQuestions`, including evaluation-relevant hidden answers. The rule-based policy only receives the extracted taskDescription; **this is not evidence of actual agent answer leakage in Round 002**. It IS evidence that protected evaluator fields are present in stored artifacts and readily available for accidental agent context, retrieval or training leakage. The existing `test_no_gold_access_in_adapter` merely scans source text for certain string literals, not a dynamic tool-return allowlist. Build a trusted assessor boundary and safe serialization (future runs only); preserve original contaminated calibration artifacts and exclude their tasks/seeds from future held-out claims.

### P0 — REACTOR LAB 2/11 MAY NOT MEASURE POLICY PROGRESS

Reactor Lab scorecard gives **2/11** from 'Reactors On', while 'Crystals Examined', 'Reactors Changed', 'Crystals Taken' are 0. Both arms of seed42 show the same 2/11. Current script does not record initial score before agent actions, nor valid action counts, so the reported nonzero score **could be an initial state / environment tick property**, not demonstrated scientific decision success. Recheck initial and final scores and compare a matched neutral/no-op control. The other three scenarios all score 0. Treat 'score variation' as superficial cross-scenario scorecard variation, not proven useful policy-driven outcome variation.

### P1 — SUCCESS label and test strength

`RunStatus.SUCCESS` is assigned whenever `final_score>0`, even if `completedSuccessfully=false`. For Reactor Lab `completed=false`, so `status=SUCCESS` confuses nonzero partial progress with task completion.

Tests assert action_count-based decision flags and that policy reasoning contains 'STRATEGY'; they do not verify legal action names, action success, counterfactual observation→action sensitivity, replayable event counts, initial-state score subtraction, or dynamic evaluator-to-agent leakage. The 82 test count is executor-reported and does not close these gaps.

### P1 — Benchmark comparison factual correction

Suitability matrix says SciAgentGym is unavailable based on searching `OSU-NLP-Group/SciAgentGym` and `scagentgym/SciAgentGym`; its real official-public candidate repo exists at **https://github.com/CMarsRover/SciAgentGYM**. Mark it `AVAILABLE_REPO / RUNTIME_NOT_EVALUATED`, NOT absent. Different DiscoveryWorld scenarios share one action engine; they are science-themed environments, not proven independent scientific domains.

## Gate decisions

| Gate | Planner verdict |
|---|---|
| R2B-01 | PASS at documentation level — R3 erratum recorded |
| R2B-02 | PARTIAL — two environments assessed, but alternative candidate incorrectly said unavailable, methodological independence overclaimed |
| R2B-03 | PARTIAL PASS — real DiscoveryWorld API invocation, but accepted action execution not proven |
| R2B-04 | **FAIL** — 14 decision flags do not imply observation-dependent actions; no step trace |
| R2B-05 | **INCONCLUSIVE** — 2/11 may reflect initial state; three task families entirely zero |
| R2B-06 | **PARTIAL** — 82/82 tests executor-reported, missing actual experimental validity and isolation tests |
| R2B-07 | CONDITIONAL only, insufficient GO for Phase1 |
| R2B-08 | Git push verified; Planner **has not accepted Round 002** |

## Scientific decision and priority

Treat the current 12-episode run as **environment boot / scorecard smoke**. No valid strategy-transfer experiment has occurred. **Do not start Phase 1 predictive/controller training** or a 30+ episode LLM sweep.

Authorize a bounded **Round 002-R1 feasibility correction**, capped at offline $0 new API charges: (1) valid action schema and accepted action traces; (2) real evidence-dependent branch demonstrated with altered observation and fixed state; (3) hidden scorer boundary and safe logs; (4) initial-score controls; (5) clean immutable audit. If the official API cannot support such research decisions reliably, return NO-GO with proof instead of another long repair loop.

Planning Round 003 or Phase 1 occurs ONLY after this validity gate is passed and a separate small LLM pilot is authorized.
