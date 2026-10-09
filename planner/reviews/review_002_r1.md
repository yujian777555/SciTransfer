# Planner Review — Round 002-R1 (2026-10-09)

**Reviewed Executor HEAD:** `31087940a3575dbb5917fd22f7d0a29932af7c11`
**Verdict:** **PARTIAL ENGINEERING ACCEPTANCE; SCIENTIFIC EVIDENCE NOT ACCEPTED.**
**Next:** `planner/plan_002_r2.md`. Phase 1 training remains UNAUTHORIZED.

## Grounded findings

Read actual GitHub source, four new traces, test source, result JSON, and upstream DiscoveryWorld API action specification. The Planner did not independently execute pytest or the environment.

1. The adapter now uses uppercase action schema and records real API responses. Candidate-safe `*_trace.json` contains serialized step events with observations, actions, and responses, substantially improving Round 002's invalid-action/no-trace problem.
2. Combinatorial Chemistry strategy arm's four `ACCEPTED` actions are successive `MOVE_DIRECTION east` navigation steps. Thereafter attempts to move east are rejected with an error expecting an object UUID, so action validity is context-sensitive and incomplete. Its baseline tries `PICKUP wall` three times then `MOVE_DIRECTION north`, all rejected. **4-vs-0 is not scientific experimentation nor evidence of scientific strategy benefit.** Archaeology arms each have one accepted movement action.
3. `EvidencePolicyAgent.decide` uses observation inventory/accessible object names, and counterfactual unit tests change accessible objects. Thus policy-level observation dependence is demonstrable. But `n_decision_points` increases on any accepted action with nonempty `evidence_used`, even movements, and no live experimental observation→hypothesis revision is shown.
4. Four initial/final task score deltas are all 0; no evidence of improved scientific outcome or cross-domain transfer.
5. The candidate-facing traces omit hidden scorer fields, **but all four full `*_trusted.json` files are tracked in this public repo and include `criticalHypotheses`/`criticalQuestions`**. The candidate/trusted classes share a Python process and API handle; this is not strong runtime/provenance separation. No proof these values influenced this deterministic rule policy, but future model exposure is a serious contamination risk. Quarantine prior exposed seeds 42,43,100 and prevent any further tracked grader data. Historical Git content remains accessible unless separately addressed; do not pretend history can be undone by a new .gitignore.
6. Different A/B policy classes are used (NoStrategyAgent vs EvidencePolicyAgent). Any action difference is confounded with different base policy capability; a strategy effect cannot be identified. Future A/B must use one identical LLM agent with only preregistered strategy context varied.
7. `results/result_round_002_r1.json` reports **21 passed / 0 failed / 1 skipped** for R1 tests, plus 82 previous tests. `status.json` agrees on 21/22. The chat claim `104 passed / 0 skipped` is unverified/inconsistent. No single full-suite command log was included.
8. The R1 calibration script contains four episodes but no matched no-action/tick-only controls; initial=0 for tested Chemistry/Archaeology scenarios does not resolve previously exposed Reactor Lab initial-credit issue. R1 source serializes event arrays as JSON, not JSONL.

## Formal gate review

| Gate | Planner decision |
|---|---|
| R2R1-01 | PASS: additive erratum and SciAgentGYM correction |
| R2R1-02 | PARTIAL: accepted movement actions; repeated invalid moves, no substantive scientific actions |
| R2R1-03 | PARTIAL: counterfactual unit policy sensitivity, live science evidence-response not proven |
| R2R1-04 | ENGINEERING PASS: event arrays and action responses, despite JSON-vs-JSONL naming |
| R2R1-05 | **NOT MET**: trusted grader content committed publicly; weak isolation boundary |
| R2R1-06 | PARTIAL: selected initial scores measured; neutral control absent |
| R2R1-07 | PARTIAL: 4 runs, disputed full pytest count and 1 reported skip |
| R2R1-08 | Repo push verified, Planner does not certify full round |

## Decision

**Conditionally authorize the smallest possible paid model action-planning pilot** at most **4 paid episodes and USD 1 aggregate additional API expense**, only after the mandatory offline G0–G2 integrity, fairness, and meaningful-action checks in `planner/plan_002_r2.md` all pass. If any gate fails, **ZERO LLM CALLS** and return BLOCKED/NO-GO. No Phase 1 predictor/controller training or cross-domain transfer claims are authorized. This is the final bounded Phase0-B feasibility probe absent genuinely new evidence.
