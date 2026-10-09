# SciTransfer — Planner Round 004 (Phase 0-D): Controlled Scientific Transfer Research Design Only

**Issued:** 2026-10-10
**User authorization:** explicitly approved “B route” method redesign after the failure of SciAgentGYM as an outcome-grounded research benchmark. **This is authorization to DESIGN and REVIEW, not to automatically train, use paid API, or run target trials.**
**Planner:** ChatGPT. **Executor:** Kimi/MiMo.
**Repo:** https://github.com/yujian777555/SciTransfer, branch main.
**Base reviewed HEAD:** `85ceb01c12e89c03c4906459efacc4752b6cfb2b`.
**Project identity:** process-level scientific strategy transfer, negative-transfer estimation, selective abstention. Original `planner/PROJECT_CHARTER.md` unchanged.

## Mandatory input and scientific framing

Read `status.json`, `planner/PROJECT_CHARTER.md`, `planner/reviews/review_003_r2.md`, `research/phase0d_method_proposal.md`, `research/phase0d_related_work_novelty_audit.md`, `research/phase0d_experiment_protocol.md`. Treat these three new research docs as proposed methodology, NOT validated model/benchmark conclusions.

SciAgentGym/ICML 2026 already covers scientific tool-use transfer; Memory Transfer Learning/arXiv 2604.14004 covers abstraction level and negative transfer; MCMA/ACL 2026 covers memory abstraction across task domains; Metacognitive Steering/arXiv 2609.16245 touches scientific judgment control. Never claim the general ideas are new. Do not confuse a controlled simulator with external-world scientific outcomes.

## Round 004 deliverable: research design + reviewer-style feasibility audit, **NO implementation**

Track A — DESIGN REVIEW: critique the three proposed mechanisms (batch-confounded differential expression, reaction-condition optimization, GIS/spatial sampling). Create for each: causal diagram or DAG spec, observation/action/state contract, domain-specific mathematical DGP, objective and deterministic external scoring, noise/confounding mechanism and distinct failure modes. Explicitly try to falsify the independence of these domains and devise anti-toy controls.

Track B — METHOD: write paper-grade `research/round_004_method_draft.md` including problem formalism (source traces, conditional abstract strategy, outcome-grounded paired interventions, selective risk-aware abstention), pseudocode for source-only extraction and selector, algorithm constraints, information boundary, complexity; distinguish simple hand-written source-less rules from a **strategy learned on source trajectories**. Do NOT fake learned weights, empirical results, accuracy or scores.

Track C — NOVELTY: write `research/round_004_novelty_matrix.md`. Read primary sources for at least SciAgentGym/SciForge, Memory Transfer Learning, MCMA, Metacognitive Steering, Co-Scientist, ResearchClawBench, and other charter-listed comparisons (Robin, AI Scientist, PrimeScientist, COGTRL, EvoScientist, MARS). Per work: verified bibliographic identity, exact overlapping claims vs defensible gap, public implementation/evaluation and weak points. Mark unverified papers as UNVERIFIED; do not invent. Conclude GO/CONDITIONAL/NO-GO on novelty with narrow contribution claims, no “first” and no speculative publication acceptance.

Track D — EXPERIMENTAL DESIGN: write `research/round_004_experiment_matrix.md`: factorial mechanism shifts, source-target/LODO splits, 4+ baselines, prompt-length equalization, placebo/negative transfer, abstention, paired budgets and randomization, nonfloor requirements, independent prereg commit workflow, independent test task generators, leakage canary through real loader, exact scorer/trace data versioning, paired uncertainty/statistical power proposal and realistic API-cost ranges as formula and assumptions, not fake prices.

Track E — ENGINEERING BLUEPRINT: write `engineering/round_004_design_spec.md` with directory layout, interface definitions, separate trusted/candidate processes and evaluator access control, deterministic RNG plan (adaptive action order should not break coupling), generator verification/test plan, smallest offline CPU pilot and build/scope estimate. State what can be reused from SciTransfer and what MUST NOT be reused from failing SciAgentGYM/DiscoveryWorld scoring. Propose an optional real scientific reference evaluation (source/rights/risks) before publication-grade claims.

Track F — INTERNAL DESIGN REVIEW: `planner` alone has acceptance authority. Executor prepare `research/round_004_design_decision.md` with independent critical objections, rubric DESIGN-01..06 PASS/PARTIAL/FAIL supported by text links, actual time spent and open questions. No code/tests unless needed to read sources or check documentation; any claim of test execution needs raw logs.

## Hard limits

- **Zero API cost; zero model training; zero GPU compute; no creation of real scored target episodes; do not build a large benchmark in this round.**
- Do NOT backdate preregistration, overwrite Round001–003 raw results, expose gold or rewrite status history.
- Do NOT run a scientifically unrealistic reward function depending on strategy IDs or force negative transfer by labeling mismatched-domain as bad.
- Preserve `.gitattributes` plain Git JSON/Markdown so Planner can fetch status/reports. Never reintroduce a global Git-LFS filter.
- Do not silently replace the project's original research claim, or claim simulated workflows are real experimental evidence.
- Proposed 3 domains are candidates, not proved independent. If no credible mechanism diversity and external-validity bridge exists, return a defensible **DESIGN NO-GO** rather than write more code.
- New expected results are a **design decision**, not numerical transfer outcomes.
- Do not activate Phase1, autonomous next-round loops or a paid DeepSeek test without a new explicit Planner plan.

## Artifact contract and status

Required files:
`research/round_004_method_draft.md`,
`research/round_004_novelty_matrix.md`,
`research/round_004_experiment_matrix.md`,
`engineering/round_004_design_spec.md`,
`research/round_004_design_decision.md`,
`results/result_round_004_design.json` (a design-status record; if using current result schema, must comply, with runs=[] and no fake scores),
and updated `status.json` preserving existing unknown fields.

Commit/push main and report final full SHA, actual document contents, completed vs blocked design gates DESIGN-01..06 and recommended smallest implementation milestone. Set `AWAITING_PLANNER_REVIEW` only after all deliverables exist and are plain-Git readable. Planner may then approve **a separate, bounded offline CPU prototype**; this plan alone gives NO implementation authorization.
