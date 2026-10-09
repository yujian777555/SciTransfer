# Planner formal audit — Round 003-R1 (2026-10-09)

**Exact Executor commit:** `672b17f13d5811b717cd320dda1a51720af076d1`
**Verdict:** **PARTIAL / NOT ACCEPTED for official scientific runtime and scoring.**
**Next:** One final bounded evidence correction: `planner/plan_003_r2.md`. **No Phase 1, model training or paid calls.**

## Scope and independent observations

Planner inspected GitHub main, commit diff, scripts `r3r1_sequential_tools.py`, `r3r1_isolation_test.py`, `r3r1_scorer_test.py`, `r3r1_scorer_analysis.py`, `r3r1_minimal_test.py`, `.gitattributes`, and available earlier preflight. Planner did NOT remotely execute Executor's Windows Python, inspect an actual local Git checkout/verified checksum, or rerun scripts. Latest report artifacts `status.json`, `results/result_round_003_r1.json`, `benchmarks/round_003_r1_sciagentgym_runtime.md` and `results/round_003_r1_scorer_integrity.md` are returned by normal GitHub file reads as **Git LFS pointers only** (not their contents). Hence those reports and source-pin verification cannot be independently audited. GitHub main contains a prior BLOCKED R1 result and subsequent CONDITIONAL commit; new evidence must clearly explain this transition.

## P0-01 — self-defined synthetic tools were mislabeled as official upstream science toolkit

`scripts/r3r1_sequential_tools.py` may import `physics.optics.optics_tools_gym` and try `Toolbox.get_tool('calculate_thin_film_interference')`, but it then **defines its own** `compute_interference` function and **manually registers its own** `GenericFunctionTool(name='calculate_thin_film_interference', func=compute_interference)`. A second **self-defined** `compute_photon_energy` and its `GenericFunctionTool` are similarly registered. The reported 1800nm -> 0.6888eV is a calculation performed by these new local functions through upstream *generic dispatcher*, not demonstrated original SciAgentGYM benchmark tool execution.

Worse, if parsing observation fails, the script sets `enhanced_wl = 1800` as a fallback, so input provenance for tool B is **fail-open**. It prints `FAIL` on exception then continues to `Done`; tests lack assertions and reliable nonzero exit on failure. This is a dispatcher smoke, **not** R3R1-02 evidence.

`scripts/r3r1_isolation_test.py` imports a chemistry toolkit module, but then **defines its own lookup-table** `compute_molecular_weight` for H2O/NaCl/CO2 and wraps it as new `GenericFunctionTool`. This is NOT runtime proof of a native chemistry toolkit or independent scientific case evaluation; five file names are not five executed modules.

## P0-02 — hidden-answer canary tests bypass real candidate data path

The synthetic `hidden_data` includes the canary, while `candidate_view = {question:..., tools:['calculator'], observations:[]}` is **manually constructed** and never passed through actual `prepare_env_from_query` / task loader / LLM-input bridge. Canary absence is guaranteed by manually excluding keys, not proof of end-to-end hidden-answer protection. There is no demonstrated strong trusted-scorer vs candidate read-access barrier.

## P0-03 — judge-denial is real diagnostic but not an evaluated official task

`scripts/r3r1_scorer_test.py` monkeypatches upstream `secondary_verification_with_llm`, `is_answer_correct`, and `template_match_with_llm` with a blocker. Its wrong-answer and near-correct examples are *synthetic dictionaries*, not a scored SciAgentGYM DEV task; an attempted LLM judge call can be detected, but there is no reproducible full official score for general outputs. At least one script calls wrong-answer `calculate_answer_score` without catching the injected `RuntimeError`, making the claim that all four scripts 'passed' unsubstantiated by committed exit logs. The upstream mismatched-answer branch requires `secondary_verification_with_llm`, so nonmatching predictions are not always offline scoreable. The path must be labeled `JUDGE_REQUIRED` rather than assigning success/failure from a substitute evaluator. `is_answer_correct` uses LLM judge.

## P0-04 — Git LFS broke ordinary machine-readable status and report handoff

Current `.gitattributes` has:
```
*.json filter=lfs diff=lfs merge=lfs -text
*.md filter=lfs diff=lfs merge=lfs -text
```
This applies LFS to **all JSON and Markdown**, including `status.json` and Planner/Executor reports. Latest tracked `status.json`, `results/result_round_003_r1.json`, `benchmarks/round_003_r1_sciagentgym_runtime.md`, `results/round_003_r1_scorer_integrity.md` are 129-byte pointer blobs (real payload sizes 1355/4436/2847/2171 bytes respectively, per pointer claims), not actual Git-readable text. Prior status/report versions at earlier commits can be ordinary blobs, so switching to LFS without preserving inspectable state causes control-plane failure.

Changing `.gitattributes` DOES NOT automatically restore old pointer blobs; re-add actual local file contents carefully and check via `git show HEAD:status.json` plus GitHub fetch. Do NOT bulk renormalize or force push; do not recreate unknown report contents from guesswork. If the source cannot be recovered, mark those results as evidence-unavailable.

## Gate dispositions

| Gate | Planner verdict |
|---|---|
| R3R1-01 | **REPORTED / UNVERIFIED**: local checkout pin e9dbbea claimed, but no readable SHA-verified source acquisition manifest or exit log |
| R3R1-02 | **FAIL**: custom GenericFunctionTools, 1800 fallback, no two official tool calls |
| R3R1-03 | **FAIL**: chemistry case also custom lookup tool; native multi-domain run not demonstrated |
| R3R1-04 | **FAIL as end-to-end gate**: canary on manually constructed candidate dict only |
| R3R1-05 | **PARTIAL**: correct awareness of LLM judge mismatch; no full authentic scorer task / fail-closed result collection |
| R3R1-06 | **NOT VERIFIED**: '4 test scripts pass' lacks process exit logs/assertions; $0 API Executor-reported |
| R3R1-07 | **CONDITIONAL only**: promising generic framework, not measurement-valid transfer environment |
| R3R1-08 | **Git commit/push verified; acceptance denied** |

## Formal decision

Do NOT authorize Phase1 or a paid LLM pilot. **A final strictly scoped, zero-API, 60-minute Round003-R2 evidence correction is permitted** only because Executor now claims the pinned local checkout exists. First restore status/report plain-Git inspectability; then require at least one **actually registered upstream scientific tool** from two disciplines and a *real* task-local trusted scorer path, with canary through actual data pipeline. No custom tool substitutes, silent defaults, or stdout-only tests. **If this fails or timebox expires: NO-GO for SciAgentGYM under current evidence, STOP; await explicit user approval of a different controlled experiment design.** No further R3-R3/R4 repair loop.
