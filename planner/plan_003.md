# SciTransfer — Planner Round 003: Phase0-C Measurement Validity / Benchmark Decision

**Issued:** 2026-10-09  
**Planner:** ChatGPT  
**Executor:** Kimi/MiMo  
**Repository:** https://github.com/yujian777555/SciTransfer, `main`  
**Reviewed HEAD:** `b05c446162c65e129185e20936b514c93ab552f6`  
**Review:** `planner/reviews/review_002_r2.md`  
**Status:** OFFLINE RESEARCH GATE; **$0 paid model calls**, no Phase1 training.  
**Budget:** at most 2 hours of bounded installation/integration troubleshooting; avoid huge downloads without user consent.

## Why Round 003 is needed

The 4-score Round002-R2 pilot is NOT an accepted pre-registered transfer experiment: pre-registration is only committed together with results and its timestamp is later than the final commit time; G1 diagnostics used target seed200; actual v2 strategy text/max tokens/steps differ; full raw LLM and scoring traces are absent; canary builder was not used in the actual runner; test log contains placeholder. Its 0/0 results are a **configuration and measurement feasibility failure**, not a falsification of the SciTransfer central hypothesis.

**Do not spend money polishing DiscoveryWorld prompts again in this round.** This is one sharp validation of whether a better measurement environment exists. If not, escalate a research-design decision to the user and Planner; don't do Round003-R1/R2 endlessly.

## Scientific north star, unchanged

Keep `planner/PROJECT_CHARTER.md`: learn process-level scientific research strategies from source scientific domains; test with *paired interventions* on held-out tasks/domains whether strategies change **verified scientific outcomes**, and abstain when negative transfer is likely. Domain/tool names and more prompt text are not sufficient scientific strategy. Do not silently replace the charter with generic tool-use accuracy. If changing the previously targeted bioinformatics/chemistry/GIS mix, provide a documented alternative and request user/Planner approval; do not represent unapproved substitutions as completed transfer evidence.

## Track A — Freeze and audit all Round002 evidence (no retroactive repairs)

1. `git pull --ff-only`; verify commit and clean worktree. Preserve all old R2 files byte-for-byte. Add `results/round_002_r2_erratum.md` citing exact issues: prereg timestamp `2026-10-09T22:00:00Z` > final commit `13:42:28Z`; same-commit first appearance; G1 seed200 was also a target; actual `v2` strategy/steps/tokens mismatch; prior scorecard leak; only aggregate outputs; incomplete `[to be filled]` test log; cost estimate vs authentic bill; call errors/fallback to MOVE east; missing neutral control.
2. Explicit labels: `UNVERIFIED_PROSPECTIVE_REGISTRATION`, `UNVERIFIED_EPISODE_TRACE`, `UNVERIFIED_API_USAGE_COST`, `CONFIGURATION_MISMATCH`, `NO_VALID_SCIENTIFIC_TRANSFER_COMPARISON`. Do not claim fraudulent API billing or fabricate original time/usage, and do not overwrite old results.
3. Scrub future candidate datasets: hidden answers already visible in Git history and previously diagnostic seed200 => quarantine. Preserve immutable provenance/manifest only, no further hidden scorecards in public repository.
4. Re-run all local tests (where possible) with redacted `pytest` output and actual pass/fail/skip counts. If dependencies unavailable, mark BLOCKED rather than claiming a pass.

## Track B — ONE targeted SciAgentGYM feasibility audit ($0, bounded)

Candidate: **https://github.com/CMarsRover/SciAgentGYM** — actual public repo, README describes multi-step scientific tool use, typed tools in physics, chemistry, materials, life science and automated answer verification. This is a **candidate**, NOT yet confirmed installable or suitable for outcome-grounded strategy transfer.

1. Pin exact upstream Git SHA, inspect legal terms and assets; make a clean authorized local checkout OUTSIDE the SciTransfer Git tree. Avoid any protected data copying and API secrets.
2. Do static inspection of `gym/env.py`, `gym/core/evaluator.py`, `gym/core/tool_loader.py`, `gym/test_querys.py`, sample cases, and tool schemas: identify real action/observation/tool execution, reset/seed support, unmodified scorer semantics, source/target task splits, hidden `answer`, `golden_answer`, `solution_steps` and `tool_expected` risk.
3. Timebox environment build to ~2h total. Start with one small text-only example requiring at least **two actual sequential scientific tool calls**. Record executable commands, elapsed, typed arguments, outputs, exceptions, environment/container details. Where possible test exact scorer with a known invalid output and public example, as **dev-only** scorer sanity; do NOT grant candidate code access to hidden reference answer.
4. If that works, try at most one similarly small dev task in a second distinct discipline (e.g., chemistry and physics, or chemistry and life science). Keep any gold-answer oracle in a trusted separate evaluator context, never in candidate prompt/tool logs. No paid LLM; use documented offline hand-selected valid tool invocations for mechanical feasibility, labeled as such. Do not call this an agent success-rate study.
5. Compare explicitly to DiscoveryWorld and ScienceAgentBench on *scientific methodology*, reproducible outcomes, step decisions, intervention feasibility, hidden answer boundary, evaluation reliability, hardware cost. Do not claim distinct disciplines based on labels alone.
6. If installation or tool execution cannot run within timebox, stop and record evidence; do not spin up massive training or reinstall for days. Mark candidate `NOT VERIFIED` or `NO-GO` by demonstrated reason.

## Track C — precondition for any future strategy-transfer test (design only)

Develop a **falsifiable preregistered prospective protocol** (no scored target runs now), including:
- At least 3 defensibly distinct scientific discipline families or explicitly reject cross-domain claims until available.
- Source vs target tasks strictly disjoint (task templates and hidden solutions separated). Source can provide learned process strategies; target only receives allowed tools/context.
- Strategy representation `(preconditions, research_action, expected_evidence, failure_conditions, cost)` extracted from **source** traces, not directly from hidden gold.
- Arms: same agent, model, tool access, initial state, and budget; A=no strategy, B=source-learned conditional strategy, C=length-matched placebo/generic guidance where feasible, D=abstain/negative transfer gate only when labels exist.
- Task-local scientific process verifier and official outcome verifier; explicit `action` vs `evidence` vs `score` chain, matched seeds and run IDs. Instrument genuine repeated experimental decision changes rather than movement.
- True **pre-run independent commit** of plan/config and hashes, before collecting scored target traces. Honest UTC timezone and version/provenance. Model messages, tool events, per-call usage and costs saved safely; no guessed billing presented as actual.
- Transparent floor/ceiling feasibility thresholds and early stop; no retrospective deletion or cherry-picking.
- Counterexamples for spurious transfer, including mismatched strategy, negative-transfer control and abstention. NO model training without outcome variation and sufficient paired labels.

## Deliverables and acceptance

- `results/round_002_r2_erratum.md` and `results/round_002_r2_evidence_inventory.md`.
- `benchmarks/round_003_sciagentgym_feasibility.md`: executable source/version, dependencies, command and log proof, true tool/scorer examples or blockers; task/domain matrix and gold leakage audit. Do not commit unlicensed assets, hidden gold, or giant datasets.
- `research/round_003_identification_protocol.md`: scientific causal identification, controls, transfer/negative-transfer, source-vs-target split, prereg/provenance and feasibility stopping rules.
- `results/result_round_003.json`: exact states, audit results, actual test counts, budget ($0) and blockers.
- Updated `status.json`, commit and push main. Review awaited.

**Round 003 gates (Planner only):**
- **R3C-01** truthful additive R2 erratum and historical preservation.
- **R3C-02** SciAgentGYM source pinned, ability to build/run realistically verified or honestly BLOCKED.
- **R3C-03** actual 2-step scientific tool execution and trusted scorer demonstrated in a safe dev task, or NO-GO with evidence.
- **R3C-04** second science discipline inspected/run and domain independence qualified.
- **R3C-05** hidden solution cannot leak into candidate context; tests for nested gold fields and result export.
- **R3C-06** approved prospective transfer design with matched arms/negative controls/abstention and proper separate prereg commit protocol.
- **R3C-07** full tests, commands, local resource cost, and reasonable stop; no paid LLM calls.
- **R3C-08** honest research verdict `GO / CONDITIONAL / NO-GO`, Git push, Planner acceptance pending.

**Stopping condition:** If SciAgentGYM has no working trustworthy outcome-grounded task under timebox, or produces only answer-matching without controllable research-decision interventions, choose NO-GO for this candidate. Propose at most one *methodological* alternative for Planner/user decision (e.g., a minimal controlled multi-domain experiment simulator with external evaluation), without auto-launching a new research program.

**No Phase 1 training; no further paid API calls in Round 003.**
