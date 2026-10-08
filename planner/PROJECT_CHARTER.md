# SciTransfer — Research Charter (Planner-controlled)

## Central question

Can process-level scientific research strategies learned in one domain **causally improve** research outcomes in another domain, and can an agent abstain when transfer is predicted to be harmful?

This is not a new generic multi-agent research system. It is an **empirical research agenda** with a conditional method contribution if supported by real experiment.

## Provisional research questions

- **RQ1 Transfer:** Under controlled agent/model/tool/initial-state/budget conditions, which strategies improve outcomes in unseen scientific domains?
- **RQ2 Abstraction:** Compare raw trajectory, task-level lesson, subtask tactic, and state-conditioned conditional strategy; do not assume deeper abstraction is better.
- **RQ3 Selective transfer:** Does utility-calibrated strategy selection with an explicit abstain action reduce negative transfer relative to simple retrieval or ungated strategies?

### Example strategy schema

`{id, source_domain, preconditions, research_action, expected_evidence, invalidity_conditions, cost_constraints, provenance}`.

An abstract research tactic is NOT a tool name such as `run_DESeq2`. Examples: replicate before escalation after inconsistent results; test cheapest discriminating baseline; audit metrics before accepting a surprising gain.

## Related-work collision guard

Relevant comparisons must explicitly include or discuss Co-Scientist, Robin, AI Scientist, PrimeScientist, Metacognitive Steering, COGTRL, EvoScientist, MARS, MCMA, Memory Transfer Learning, and scientific-agent benchmarks. **Do not claim first** for scientific policy optimization, persistent memory, cross-task skill transfer, abstraction-level memory, or negative transfer without a separate up-to-date verification.

Primary resources to verify before running:
- ScienceAgentBench: https://github.com/OSU-NLP-Group/ScienceAgentBench
- DiscoveryWorld: https://github.com/allenai/discoveryworld
- ResearchClawBench: https://github.com/InternScience/ResearchClawBench
- MCMA: https://aclanthology.org/2026.findings-acl.1535/
- Memory Transfer Learning: https://arxiv.org/abs/2604.14004

Links are pointers for verification, not a claim of current installation, license compatibility, dataset availability or reproducibility.

## Critical identification issue

Observational trajectory performance ≠ causal transfer utility. **Paired interventions** must use the same task, agent, tools, initial environment state, and matched budgets, altering only the strategy intervention. When stochastic, pre-register matched seeds and repeated trials. Report paired differences with uncertainty and include strategy-token/cost overhead. A matched-length neutral prompt arm is desirable to separate added context from actionable strategy.

Historical traces may be used to **extract candidates**, but should not be presented as counterfactual utility labels.

## Scientific honesty / anti-leakage

No use of hidden test solution materials during strategy extraction or selection; predeclare source/target split and template/seed isolation. Judge-based ratings are secondary to official executable task scores. A negative or null transfer result is publishable as a research finding if the measurement is rigorous; do not manipulate task inclusion or metrics to manufacture success.

## Roadmap decision gates

- Phase 0: runnable/restartable environments, valid paired-run evidence, official evaluation, cost trace.
- Phase 1: initial transfer matrix and abstraction-level comparison; uncertainty and meaningful controls.
- Phase 2: ONLY if Phase 1 signal and sufficient labels: train utility predictor/abstention gate and evaluate held-out target tasks.

**Do not proceed past the current plan without Planner acceptance.**
