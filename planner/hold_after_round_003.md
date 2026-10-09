# SciTransfer — Planner Decision Hold After Round 003

**Date:** 2026-10-09  
**State:** **BLOCKED — Awaiting user/external-source decision**  
**Last reviewed Executor SHA:** `15ce557c994c1dcd38dec66837fa2359ba9db4e1`  
**Formal review:** `planner/reviews/review_003.md`  
**This is NOT an executable Round 004 plan.**

## Why work is paused

Round003 delivered an evidence-accurate ten-item R2 erratum and a draft cross-domain experiment identification protocol. However, SciAgentGYM has **not** been cloned/installed locally, and no actual sequential tool+score workflow has run. Current source inspection also showed `calculate_answer_score` can invoke an LLM judge on mismatches; claiming always-offline official evaluation is unsafe. The platform has an Apache 2.0 root LICENSE but third-party content terms remain to be checked.

**No Phase1 training, no new paid API runs, and no broad infrastructure refactoring are authorized.** `current_round=3` intentionally remains unchanged.

## Exactly one user decision is needed

**Option A — unblock SciAgentGYM access (preferred if practical).** Provide the Executor with a legal, verified source checkout/archive of upstream commit `e9dbbea4369d67694e38bf8be67bedbcaf9e9300` and a locally accessible Python 3.11/conda environment or reliable network/mirror access. Keep checkout OUTSIDE SciTransfer. Executor should NOT clone or install again until the user has confirmed the actual source route. After confirmation, Planner can issue a one-time offline smoke plan with 2h hard timebox and $0 paid API, testing one physics/chemistry task then a second discipline, including actual two-step tool calls, schema, hidden gold partition, and evaluator fail-closed LLM-judge behavior. No synthetic 'official scores'.

**Option B — explicitly approve a method-level redesign.** If SciAgentGYM cannot be executed safely within available resources, ask Planner to propose a **minimal, controlled multi-domain scientific-process simulator with external deterministic scoring**, preserving the SciTransfer central hypothesis (process strategy source→target, potential negative transfer and abstention). Any new tasks/metrics/domain substitutions require fresh preregistration and explicit user consent. This is an alternative research program design, NOT equivalent evidence to the original published benchmark.

**Option C — park SciTransfer.** Wait until external environment access is available. No Executor activity required.

## Non-negotiable next validation after user decision

1. Record exact external source SHA/license and actual local dependency/runtime fingerprint.
2. Demonstrate two successful consecutive scientific tool calls in a real task with observable information-dependent choice; no hidden answer access to candidate.
3. Demonstrate evaluator semantics with perfect, wrong, missing and near-correct dev examples, including whether `secondary_verification_with_llm` is called. Any offline scorer modification disclosed and benchmark scores labeled accordingly.
4. Verify the second scientific domain has executable tools and enough distinct tasks; do not treat tool-category names as domain-generalization proof.
5. Only after authentic runnable outcomes and floor/ceiling checks, develop source→target strategy acquisition/causal matched-arm prereg plan as an **independent earlier Git commit**.
6. New LLM requests, training and official research effect statements still need separate Planner signoff.

## Stop

No new `results/result_round_004.json` expected now. No forced Git pushes, rewriting historical scores, exposing gold or requesting API keys. Executor waits for user instruction.
