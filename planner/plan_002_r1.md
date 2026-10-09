# SciTransfer — Planner Round 002-R1: Genuine Scientific Action & Evidence-Conditioning Gate

**Issued:** 2026-10-09  
**Planner:** ChatGPT  
**Executor:** Kimi / MiMo (record actual agent and environment)  
**Repository:** https://github.com/yujian777555/SciTransfer  
**Branch:** main  
**Reviewed commit:** `33d51a095fa9fc98ea3fcbec3669fbc96c99a747`  
**Review:** `planner/reviews/review_002.md`  
**Phase:** PHASE0-B / Round 002-R1, not Phase1.  
**Scope:** **minimal correction only**, $0 paid API, no model training.

## Goal

Prove DiscoveryWorld can support a meaningful, budget-controlled scientific decision **from observation/evidence to a valid next action**, with hard isolation between evaluator hidden information and candidate agent. Old Round 002 data remains a *smoke test*, not actionable efficacy evidence. Do not launch a broad sweep. If fails after a bounded attempt, document NO-GO and propose an alternative rather than iterating indefinitely.

## Track A — Freeze prior artifacts and correct the paper record

1. Pull latest `main`; read `status.json`, formal review, `planner/latest_plan.md`, and current source. Preserve all `results/round_002_calibration/` and `results/result_round_002.json` **unchanged**.
2. Create `results/round_002_erratum.md` with line-accurate evidence: invalid action JSON names/arguments; the decision count based only on step number; serialized n_actions=n_observations=0; hidden `criticalHypotheses`/`criticalQuestions` in committed scorecards; Reactor Lab 2/11 unproven attribution; `SUCCESS` despite `completedSuccessfully=false`; wrong SciAgentGYM URL. Mark old seeds 42/43 and episodes *quarantined from future held-out evaluations/training*.
3. Fix `benchmarks/suitability_matrix_round_002.md` **additively via dated correction** or create `benchmarks/suitability_matrix_round_002_r1.md`: https://github.com/CMarsRover/SciAgentGYM is public but not yet installed/tested. Do not conflate scenario themes with proof of scientific domain independence.

## Track B — ACTION JSON correctness and action success instrumentation

1. Pin exact DiscoveryWorld package/source revision and record `DiscoveryWorldAPI.listKnownActions()` plus `additionalActionDescriptionString()`. Use **actual upstream enum** such as `MOVE_DIRECTION`, `PICKUP`, `USE`; use direction in `arg1`, object UUIDs in `arg1`/`arg2` as specified. Never invent camelCase actions. Resolve object IDs from **allowlisted, actual public observation/UI data**, not hidden world internals.
2. Add a strict action schema validator before `performAgentAction`: reject unknown action, missing/wrong argument type, inaccessible UUID, and wrong direction without ticking it as a successful scientific decision.
3. Record `performAgentAction` response (`errors`, `success`, message); distinguish `parsed`, `accepted`, `environment_changed`, `evidence_acquired`. Count successful actions; report `n_valid_actions`, `n_invalid_actions`, and their raw reasons; invalid actions cannot count as meaningful decision points.
4. For at least 2 real scenario families, demonstrate at least TWO accepted and state-influencing actions per episode; if impossible, report BLOCKED and factual API limitations. Don't hardcode task-specific answer locations.

## Track C — Prove actual observation-dependent decision-making

1. Rewrite `SimplePolicyAgent.decide` (or implement a minimal separate `EvidencePolicyAgent`) such that **actual observation contents or last action result** determine which next action it selects. A step-count script is insufficient.
2. Add **counterfactual decision tests**: at identical state/step/history except for one visible observation change, the candidate chooses a different valid action, with reason tied to an actual observed cue. Require evidence of accepted action outcome or state/evidence change before counting the next decision.
3. Explicitly compare NO_STRATEGY vs FIXED_CONDITIONAL_STRATEGY on the *same observation sequence*; show strategy changes some action choices for a defensible observable condition, not only the reasoning suffix. Keep arms same legal action set and max steps/time.
4. Every episode must produce a complete immutable per-step JSONL: observation (sanitized), proposed and validated action JSON, action response success/error, environment tick, next observation, action rationale, timestamps or monotonic offsets, strategy ID/hash, scenario/seed, and event checksum chain or strong per-file SHA. `n_observations` and `n_actions` must reconcile with serialized events; no silent truncation of full evidence.
5. Define decision point by counterfactual/evidence condition and actual transition; DO NOT use `action_count>=2` as proxy.

## Track D — Prevent evaluator/gold answer leakage

1. Split roles: **TrustedEvaluator** may call `getTaskScorecard`, but **CandidateAgent** only receives explicitly allowlisted task description, observations and action responses. Never expose `criticalHypotheses`, `criticalQuestions`, subtask `associatedNotes`, internal world object IDs invisible to the player, or raw scorecard as an agent tool response.
2. Implement a runtime tool/schema boundary and redaction before logging any prompts, observation serialization, tool outputs or future memory. A mere substring search in Python source is NOT a leakage test.
3. Unit and runtime integration tests inject canary strings into mock `criticalHypotheses`/`criticalQuestions`, scorer-only fields and hidden answers, then confirm these never enter candidate-facing observations, calls, decisions, text logs or exported public traces. Trusted scorer audit may be retained **outside** candidate-visible/searchable artifacts, with protected separate path / restricted handling.
4. Do not delete/overwrite historical Round 002 scorecards; mark them **quarantined** as contaminated with scoring guidance, and never use seeds 42/43 in future held-out inference after exposure.

## Track E — Real run, initial-score control, and calibrated acceptance

1. Compute and persist **initial score BEFORE first action**, and final score after actions, plus task completion flag and each scored subcomponent. Determine whether Reactor Lab 2/11 was already present initially by running exactly the original seed in an **audit-only** sanity check. Historical files remain untouched.
2. Run one matched neutral control that advances the environment without substantive agent actions or uses a legitimately supported WAIT action (if one exists). Compare score delta, not just absolute final score. NEVER invent an unsupported `WAIT` action.
3. New actual micro-pilot: **2 scenario families × 2 arms × 1 seed = 4 episodes**, plus ≤2 diagnostic control runs. No LLM/API calls. Choose task families prospectively from practical environments; don't cherry-pick only Reactor Lab based on observed positives as if it were an unbiased test set. Score meanings are within scenario; report normalized outcomes and initial/final separately.
4. Demonstrate valid action/evidence transitions; require at least ONE episode with a decision clearly changed by a previous observed consequence (not step count), and at least two families with a valid action sequence. An action that only moves, waits or triggers unrelated partial credit is not sufficient evidence of scientific strategy reasoning.
5. Explicitly report per-arm action success/invalid counts, baseline initial score and score delta; do not claim an effect if both arms identical or score floor persists. Report all failed/timeout attempts and actual execution costs/time.

## Track F — tests, files and stop rule

Required tests:
- upstream action schema compatibility using `listKnownActions`;
- bad action JSON correctly rejected; per-step errors preserved;
- counterfactual observation causes different, valid next action at same decision state;
- stepwise logs action/obs parity and replayability, no falsified `n_decision_points`;
- trusted evaluator canary never reaches candidate or agent-memory exports;
- initial score vs no-op score delta (detect Reactor Lab initial credit);
- status semantics: task complete vs partial score; same budget and scenario/seed for A/B;
- stable manifest/version/hash, bounded retries and no hidden answer path.

**Deliverables**
- `results/round_002_erratum.md` and corrected candidate suitability note.
- `src/scitransfer/` corrected adapter/policy with runtime tool boundary and state-aware decisions.
- `tests/` new integration tests, 82 previous tests should remain green unless explicitly repaired with justified changes (never quietly delete tests).
- `results/round_002_r1_calibration/` with real per-step event JSONL and task-level final scorer summary; exclude hidden scorer keys from candidate-readable traces.
- `results/round_002_r1_decision.md`: GO / CONDITIONAL / NO-GO on validity of multi-step benchmark, not scientific policy transfer.
- `results/result_round_002_r1.json`, updated `status.json`, commit to main and report SHA.

**Hard gates**
- **R2R1-01**: prior-score erratum + SciAgentGYM provenance correction, no old-data rewriting.
- **R2R1-02**: actual official action schema accepted; instrument successful and failed actions with evidence.
- **R2R1-03**: at least one real consequence-dependent action choice (counterfactual observation changes valid action); two families demonstrate valid multi-step action execution.
- **R2R1-04**: complete reviewable raw step traces, valid counts, API response metadata and hash/version/seed.
- **R2R1-05**: hidden grader answers never available in candidate-facing tool messages/logs or future memories; dynamic canary tests pass.
- **R2R1-06**: initial vs final score and matched neutral control; avoid interpreting ambient Reactor Lab score as agent progress.
- **R2R1-07**: all tests pass incl. real integration, report pass/fail/skip; 4 bounded new episodes + ≤2 controls, $0 API.
- **R2R1-08**: honest research decision, result and status pushed; Planner alone accepts.

**Stop immediately** if no accepted actions, hidden scoring cannot be isolated, reset is unreliable, or no observable consequence-dependent policy is feasible without a model. Return BLOCKED/NO-GO and propose one alternate benchmark (SciAgentGYM official repo can be investigated, but not fabricated).

**Phase1 is NOT authorized** in this round. Future small LLM pilot requires separate Planner authorization after R2-R1 passes; model policy utility predictor/controller training requires further evidence of a learnable strategy effect.
