# Phase 0-E — Novelty, Value and Computational Feasibility Audit (DESIGN PRE-FLIGHT)

**As of:** 2026-10-10
**Coverage:** targeted verified primary public sources, NOT exhaustive review or paper acceptance forecast.

## Direct peer-work overlaps (not novel)

- **SciAgentGym/SciForge** — Shen et al., ICML 2026, https://proceedings.mlr.press/v306/shen26aa.html ; already reports cross-domain scientific tool capability transfer. Generic multi-science tool transfer and trajectory learning are not novel.
- **Memory Transfer Learning** — Kim et al., arXiv:2604.14004, https://arxiv.org/abs/2604.14004 ; already studies cross-domain memory abstraction, meta-knowledge (including validation routines) and negative transfer. “General validation habits transfer” alone is **already a strong collision**.
- **MCMA** — Findings ACL 2026, https://aclanthology.org/2026.findings-acl.1535/ ; already discusses abstraction-level memory transfer and memory meta-control.
- **Robin**, **The AI Scientist**, Co-Scientist, Metacognitive Steering, ResearchClawBench, PrimeScientist, COGTRL, EvoScientist, MARS remain required full claim-by-claim checks, especially for selective action/abstention and paired outcomes. Do not call work UNVERIFIED after reading only a secondary summary, and do not invent exact model claims.

## Hypothesized narrow contribution (subject to falsification)

C1: **paired, outcome-grounded process strategy transfer** between genuinely different *real scientific data-analysis workflows*, using pre-frozen source-conditioned decision rules and private measured-label scoring.
C2: **causal mechanism of harmful transfer:** split leakage/diagnostics failures under domain-specific grouping shifts, tested with source and target policies and no privileged target truth.
C3: **calibrated selective transfer** only if empirical source labels support predictive reliability, otherwise abstain. No guaranteed novelty in risk-based abstention; compare strong selective-prediction and transfer-gating literature.

All three may collapse to routine leakage-safe model selection; unless an independent literature reviewer finds a nontrivial technical method and baseline comparisons support it, the work is at most an applied reproducibility study, **NOT a strong CCF B-worthy novel method**. Avoid claiming originality on the basis of changing data domains or adding prompts.

## Scope and cost feasibility

**Design-only Round006:** $0 paid LLM/API, $0 GPU; 1–2 days document/source inspection is an *estimate*, not a verified delivery promise.
**Proposed future micro-smoke (NOT AUTHORIZED NOW):** public ESOL train/DEV split + tiny NOAA station/year subset, no LLM, SciKitLearn/RDKit and geopandas/scikit-learn on CPU, or other vetted reference library. **R/Bioconductor DESeq2 as later optional lane**, separate environment/licensing considerations. Need measure data download size, install minutes, RAM, network reliability and cache availability, not assume they work.
**Future matched LLM experiment cost:** `N_tasks * N_arms * N_repeats * (average_input_tokens * price_in + average_output_tokens * price_out + retry_budget)`; no current numeric billing rates or guaranteed cost. Set explicit approved dollar ceiling ONLY after a prospective budget proposal.
**Risk:** 2 domains share superficial supervised regression mechanics; a genuine scientific-process strategy might not differ from ordinary cross-validation advice. ESOL small, NOAA data big/dynamic, airway has no exhaustive gold, and model-known public labels threaten holdout. Set hard stop early if these invalidate a causal strategy test.

## Evidence gates for design-go only

- Two independently scored real-label tasks, credible datasets and rights/reachability documented.
- Demonstrably different scientific choices and failure regimes, not two names for the same model search.
- Actual train/DEV/private test partitions and scorer contract specified without test feedback leakage.
- Source-learned conditional strategy distinguishable from generic checklists and heuristic hyperparameter search.
- Strong baselines/ablation plan and independent quantitative scoring with paired budgets.
- Narrow novelty validated against closest papers; a CCF-B target is plausible only conditionally and requires substantial empirical + technical contribution.

**Verdict today:** CONDITIONAL-FEASIBILITY-ONLY. No claim that the project is ready for experimental implementation or that it is scientifically novel.
