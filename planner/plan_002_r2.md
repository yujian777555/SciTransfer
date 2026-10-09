# Planner Round 002-R2 — Secure, Matched, Bounded LLM Feasibility Pilot

**Date:** 2026-10-09  
**Planner:** ChatGPT; **Executor:** Kimi/MiMo  
**Repo:** https://github.com/yujian777555/SciTransfer (main)
**Reviewed HEAD:** `31087940a3575dbb5917fd22f7d0a29932af7c11`
**Formal review:** `planner/reviews/review_002_r1.md`
**Phase:** PHASE0-B / Round 002-R2; **NOT** Phase 1 learned-strategy training.
**Authorization:** COND​ITIONAL, at most 4 scored DeepSeek episodes and cumulative additional API cost <= USD 1; **no LLM calls before offline G0/G1/G2 pass**.

## Scientific question and non-goals

Can the SAME LLM agent execute genuine scientific actions in DiscoveryWorld, observe consequences, adjust its next action, and receive an outcome score from a trusted evaluator? Only vary the intervention strategy text between matched arms. Fixed conditional strategy is HAND-AUTHORED, not learned or transferred. No cross-domain benefit, causal generalization, model training, or publication claim in this round.

Preserve 002 and 002-R1 historical artifacts, including mistakes and exposed trusted scorecards, without backdating or overwriting. Add a separate erratum and quarantine manifest.

## G0 — secrecy and isolation (mandatory; before paid run)

1. **Never track another `*_trusted.json` / full scorecard, hidden answer, `criticalHypotheses`, `criticalQuestions`, `associatedNotes`, scorer-only UUIDs or gold file.** Add appropriate .gitignore rules, store privileged audit data in restricted untracked local directory; retain only task-level numeric initial/final score, completion and provenance hashes in Git. Existing tracked trusted files contain such data: preserve original Git history and report leakage, stop tracking future updated content; do not claim that deletion removes historical exposure.
2. Quarantine all earlier exposed seeds 42,43,100, including those scenarios' known hidden hints. Pre-register fresh instance seeds before any model run; no claims of fully unseen scenarios from a public game benchmark.
3. Implement one whitelist `build_model_input(safe_task_description, sanitized_observation, allowed_action_schema, recent_public_actions)` and run candidate code/model client without scorer API handle or scorer-only file access. Prefer a separate restricted process / mediator. A class called TrustedEvaluator sharing an API object with candidate-facing code is insufficient access control.
4. Canary tests must inject nested secret markers into scorer-only fields, then verify absence of markers in **all actual model API messages**, agent memory, traces and Git-staged files. Fail closed if leakage or trusted data is observable.
5. Write `results/round_002_r1_erratum.md` documenting R1's four navigation successes vs invalid pickup, public trusted files, zero score deltas, test count inconsistency, missing neutral control and policy-class confound. Do not modify original results.

## G1 — official action semantics and real scientific decisions (mandatory)

1. Pin DiscoveryWorld version/commit and query `listKnownActions()` and `additionalActionDescriptionString()`. Confirm actual `MOVE_DIRECTION`, `PICKUP`, `USE` parsing/UUID requirements on an executing instance. Diagnose R1 error where `MOVE_DIRECTION arg1='east'` succeeds first four times then fails (error expected int UUID). Never count parsing-only success as state change; record `parsed`, `accepted`, `state_changed`, `meaningful_scientific_action` separately.
2. A scientific action = documented test/measurement/inspection/experimental manipulation relevant to task objective, with actual observable feedback. Movement, invalid wall pickup or repeated ticks are NOT scientific decisions. Prove at least one successful scientific interaction **without LLM** in one chosen scenario under allowed APIs. If impossible, stop and report NO-GO, no paid pilot.
3. Verify changed public feedback causes a **different valid next action** for the same agent state, with a real recorded before/after observation in an episode (unit-level counterfactual alone is insufficient).
4. Run at most two neutral/no-substantive-action diagnostic controls with initial and final score, using officially supported actions/tick semantics; do not invent WAIT. The Reactor Lab seed42 ambient-credit question is audit only and seed42 remains ineligible for future heldout evaluation. Prevent reward attribution to mere world ticking.
5. Capture real step JSONL OR correctly label JSON arrays; reconciled counts must not equate nonempty `evidence_used` to scientific decisions. Add integration tests for these behaviors.

## G2 — fairness, prospective pre-registration, and truthful tests (mandatory)

1. For A/B **use exactly one shared LLM agent implementation**, pinned DeepSeek endpoint/model and same observation, tool/action schema, step/tokens/time budgets, temperature, system prompt and environment reset. Treatment must be ONLY an added, pre-registered strategy instruction. Baseline must not be intentionally less competent; an optional token-matched neutral control only if budget allows.
2. Freeze and commit `experiments/round_002_r2_preregistration.json` BEFORE target evaluations. Include two scientifically distinct scenario families with real tasks (not mere game theme differentiation), newly fixed seeds NOT in {42,43,100}, arm order policy, version, strategy text/hash, prompt hashes, model params, stopping/cost rules. Record registration commit SHA in later evidence. No post-hoc seed/task selection.
3. Re-run `python -m pytest tests/ -q -ra` and save actual full output; clearly distinguish `21 passed / 1 skipped` R1 subset from overall count. Critical canary/schema/fairness tests may NOT skip. If failed, stop before model calls.
4. Enforce aggregate actual API spend <=USD 1 and max four *scored* episodes; enforce token and per-episode caps, log billing basis. Provider key configured only locally, never in repo/log/chat. No DashScope-as-OpenAI credential substitution. If cost not measurable or credentials absent, BLOCKED/zero call.
5. Gate proof in `results/round_002_r2_preflight.md`: G0/G1/G2 PASS with actual commands, test log and hashes. **Only after all three PASS may any DeepSeek request be sent.**

## G3 — paid micro-pilot (conditional)

1. Perform one minimal **unscored** action-schema smoke (counts toward USD 1 spending). Stop if repeated invalid actions or hidden markers, without proceeding to episodes.
2. Execute at most **2 scenario families × 2 arms × 1 fresh seed = 4 genuine LLM episodes**, same baseline runner and hard budgets, in separate reset environments. No training. Log sanitized model messages, tool results, evidence-linked revisions, program/version hashes, per-step tokens/cost/time, task score initial/final, completion and normalized within-scenario deltas. Trusted raw scorecards stay local/private and are NEVER uploaded.
3. Reject runs on invalid API schema, leakage, unequal model/tool/budget or retry contamination; do not manufacture an advantage from failed baseline actions.
4. Report all valid scientific actions, score distribution, matched pair differences and uncertainties descriptively. Uniform zero/no substantive science interaction => NO-GO for this environment at current budget; **do not interpret motion advantage as SciTransfer strategy efficacy**.
5. If cost/credentials or environment block access, stop and submit BLOCKED plus one minimal action. No 30/45 episodes or broad sweeps.

## Files, results and acceptance

Deliver: `results/round_002_r1_erratum.md`; candidate safe bridge and tests; `experiments/round_002_r2_preregistration.json`; `results/round_002_r2_preflight.md` and sanitized test log; `results/round_002_r2_pilot/` (if G0–G2 pass); `results/round_002_r2_decision.md`; `results/result_round_002_r2.json`; updated `status.json`; commit+push.

- **R2R2-01** no hidden evaluator data in candidate/provider/prompts/tracked Git; old exposed seeds quarantined
- **R2R2-02** official schema, actual accepted scientific actions, valid feedback-dependent decision, and baseline/neutral control evidence
- **R2R2-03** same LLM agent model/tool/budget, only strategy varies, immutable pre-registration before target evaluations
- **R2R2-04** exact test pass/fail/skip, mandatory integrations green, no silent skips
- **R2R2-05** 4 matched model episodes with true scores and replayable safe traces, OR an explicit BLOCKED if gates fail
- **R2R2-06** spend <=USD1, trustworthy provider config and redacted secrets
- **R2R2-07** hand-authored exploratory pilot only, not learned transfer; no unsupported statistics
- **R2R2-08** complete results, tests, status in main; Planner alone decides acceptance.

**Stop rule:** if G0, G1 or G2 cannot pass promptly, DO NOT use LLM. This is the final tightly scoped Phase0-B feasibility assessment before Planner considers switching benchmark or altering the method.
