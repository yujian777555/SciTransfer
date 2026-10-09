# SciTransfer Phase 0-D — Outcome-Calibrated Scientific Strategy Transfer: Method Proposal

**Version:** design-v1, 2026-10-10
**Status:** PROPOSAL / NOT IMPLEMENTED / NOT VALIDATED
**Authorized direction:** user explicitly approved route B (controlled multi-domain research-process evaluation), after R3-R2 ended NO-GO for current SciAgentGYM measurement configuration.
**Scientific charter:** `planner/PROJECT_CHARTER.md` remains the authority. No prior SciTransfer outcome indicates successful source-to-target scientific strategy transfer.

## 1. Research question and honest scope

Can **process-level scientific strategies learned only from source-domain interactive trajectories** increase independently verified outcomes on genuinely held-out scientific task families in another domain, and can an outcome-calibrated selector abstain from applying a harmful strategy?

This proposal replaces an **unreliable measurement environment**, not the scientific hypothesis. The primary study is a mechanistic, synthetic-but-scientifically-motivated *controlled experimental testbed*. It is NOT equivalent to real laboratory discovery or to official ScienceAgentBench, DiscoveryWorld, SciAgentGYM or ResearchClawBench scores. Claims must say “controlled simulated scientific workflows” unless and until an independent empirical external-validity evaluation succeeds.

## 2. Three distinct task families (candidate design, contingent on feasibility)

Each task is a stateful partially observable experimental process with an immutable hidden ground truth, bounded observations and a separate evaluator. Use nontrivial, independently coded mathematical generators. A shared action-level conceptual ontology (measure, replicate, diagnose, test, revise, commit) is useful for transfer **only if** domain-specific tool interfaces and stochastic mechanisms remain genuinely different.

**D1: Bioinformatics — batch-affected differential expression / replication.** Synthetic count/continuous measurements with treatment effects, batch confounders, heteroscedasticity and sequencing depth or replicate variance. Agent actions: allocate replicates, negative controls, inspect QC, choose validation split/statistical procedure, record evidence and commit a ranked hit list. Hidden evaluator: FDR, recall/power, sample cost, discovered true effects; score must penalize false positives and data leakage. Use plausible simulators/statistical checks and separate validation from true gene-level ground truth. No real human/patient data needed.

**D2: Computational/physical chemistry — sequential reaction-condition optimization.** Hidden nonlinear, noisy response surfaces in reaction factors (temperature, concentration, catalyst family or solvent class), interaction terms, constraints and heteroscedastic noise; simulated assays yield outcomes and uncertainty. Actions: choose condition, low-cost screen, replicate, control/check interference, fit simple surrogate, select candidate. Hidden evaluator: best validated constrained yield/selectivity, regret vs oracle, experimental cost, constraint violations. Avoid asserting chemically accurate synthesis or wet-lab predictive fidelity without real-data cross-check.

**D3: GIS/spatial science — spatial sampling and out-of-region validation.** Latent spatial fields with covariance lengthscales, anisotropy, drift, sampling bias, measurement noise and controlled shifts. Actions: allocate geographically blocked samples, test covariates, compare interpolators, choose spatial versus random cross-validation, validate new region, commit map. Hidden evaluator: held-out spatial error, uncertainty coverage/calibration, costly sample use and leakage. No actual geolocation or private location inputs needed.

**Scientific distinctness is a gate, not an assumption.** Three different variable names applied to one Gaussian bandit are INVALID. Compare causal graphs, latent variables, tool semantics, objectives, failure modes and protocol constraints across D1/D2/D3. At least two mechanism/template types per family; not just re-skinning.

## 3. Partially observable interaction contract

Define for each domain d and task i a generator H(d,i,seed) that produces protected latent mechanism theta and a candidate public initial observation x0. The candidate receives only public task text, legal action schemas and observations.

At step t: a_t = policy(public_history_t, optional_strategy); o_(t+1) = engine_d(theta, a_t, independent_conditioned_noise); decision history updates with public evidence. A final commit action yields domain-specific artifact y_hat. The trusted evaluator Q_d(y_hat, theta, heldout_noise) runs independently and produces a score/criterion vector. Candidate cannot open theta, hidden target fields, reward function code or target templates; separate execution process / strict mediation strongly preferred.

All actions emit typed status and cost; invalid actions fail closed (not silent default). Log public action, observation, rationale, tool version, cost, and timing. Store scorer-only detailed ground truth outside candidate-visible/searchable locations. Never expose deterministic seed material that allows the agent to reverse-engineer hidden targets.

## 4. Strategy representation and source-only acquisition

A strategy is NOT a tool name or fixed advice copied into a system prompt. Typed representation:
- preconditions: observable uncertainty/evidence regime, budget and risk constraints;
- decision_rule: abstract research intervention (“repeat an uncertain measurement before escalation” or “test cheapest discriminating control first”);
- expected_evidence: observable cue that supports/rules out a hypothesis;
- adaptation_rule: if result violates expectation, revise next experiment;
- invalidity_conditions: when strategy should be withheld;
- provenance: source domain, allowed source trajectories, extraction algorithm/version;
- cost: expected extra samples/tools/tokens.

Compare abstraction granularity: raw trace, task lesson, local tactic, state-conditioned causal strategy, with a matched-length placebo and no-strategy. Strategy discovery must use **source-domain training evidence only**, not benchmark hidden target scripts or oracle parameter access. Proposed acquisition: start from successful and unsuccessful source **pairs**, generate candidates, validate candidate logic on source DEV instances, freeze before transfer. No LLM training implied at design stage; source learner and comparator require separate authorization.

## 5. Outcome calibration and selective abstention

The primary paired contrast on task i is Delta_i(s) = U_i(policy+strategy_s) - U_i(policy_no_strategy), where both arms have same base model/agent, legal tools, initial task instance and matched cost/action/token limits. U is normalized **within** task using predeclared domain-specific physical quality, penalties for cost/invalid interventions, and never aggregate unrelated raw measures. Report both raw domain outcomes and normalized U.

If source-domain paired utility labels are adequate, fit a **calibrated conditional utility estimator** g(s, public_context) predicting distribution of Delta. The selector picks transfer only if a predetermined lower confidence/quantile bound on predicted Delta exceeds an explicitly declared risk/cost threshold, otherwise abstains. Compare transfer-all, retrieval-only, random, and abstain-all. Abstain means use the **same no-strategy agent** (not skip a task or replace an episode score with a free success). Label costs and calibration reliability. The model and threshold must be trained/calibrated only on eligible source / designated DEV tasks; no fitting to held-out transfer outcomes.

*Important ordering:* First show score variation, genuine intervention, source-to-target signal and enough paired labels. ONLY THEN authorize training a utility predictor or selective policy. Until that point, g is an abstract planned component.

## 6. Identifiability and negative transfer

Same instance/seed/task, base LLM, legal action tools, initial public state, max steps, time limit, context-window and financial budget for all arms. Only strategy attachment changes. Also include prompt-length-matched placebo to distinguish extra context from strategy effect. Counterbalance arm order, use separate reset/isolated workdirs, matched randomness without shared hidden-state leakage. Never read paired counterpart's trajectory while making a decision.

Negative transfer must be **observed paired Delta below -tau**, not inferred simply because “chemistry strategy applied to GIS” sounds mismatched. Establish expected non-transfer regimes prospectively by changing **documented latent mechanism classes**, and validate that the benchmark does not hardwire favorable utility for hand-authored strategy strings. Measure false-apply harm, abstention accuracy, risk–coverage and regret; predeclare tau, stop rules and uncertainty intervals.

Critically: if negative examples are scripted to punish a strategy by name or if the outcome function directly checks strategy IDs, the experiment is invalid. Scores must depend only on actions and physical/statistical consequences, not treatment/arm identity.

## 7. External validity and publication guard

Simulation alone can support a narrow methodology claim about controlled process-strategy transfer; it cannot establish gains in real bioinformatics, chemistry or GIS research. Before any paper-level strong claim:
1. Have an independent reviewer or separate implementation audit DGPs and mechanism asymmetry, and demonstrate hidden-state non-leakage.
2. Validate domain mechanisms against published statistical or publicly available scientific examples (document provenance and licenses), not hidden benchmark solutions.
3. If feasible, add a held-out task layer using a real public dataset or verified external evaluator distinct from the synthetic development simulator. Failure to obtain this layer must be acknowledged and limits venue ambitions.
4. Publish preregistration commits, code, seed protocols, negative/null results and measured inference cost.

## 8. Research gates and what this proposal DOES NOT prove

G0 DESIGN: mechanisms genuinely distinct; domain-specific verifiers, independent scorer and trace contracts specified; novelty collision audit and feasible cost model done.
G1 IMPLEMENTATION (not authorized now): real offline engine pass/fail/reset/replay/nonleak tests; calibration without score floors/ceilings.
G2 PILOT (needs separate Planner authorization): paired source/target intervention with independent preregistration and real numerical variation.
G3 SCIENCE: held-out transfer, mismatched controls and calibrated abstention, uncertainty and external validity.

This document contains **zero experimental results**, no demonstrated transfer advantage and no acceptance of simulator generalization to laboratories.
