# SciTransfer — Planner Round 005-R1: D1 Measurement Integrity Remediation (FINAL D1 GATE)

**Issued:** 2026-10-10 | **Planner:** ChatGPT | **Executor:** Kimi/MiMo
**Repository:** https://github.com/yujian777555/SciTransfer | `main`
**Audited HEAD:** `c9b0d7030eb53339479174c26046487b2981a81d`; formal review: `planner/reviews/review_005.md`
**Stage:** PHASE0D, repair to Round005 **ONLY**. No Phase1 transfer, no D2/D3, no strategy model/LLM, no paid API, no GPU. **$0 API**.
**Duration policy:** One bounded root-cause remediation, NOT an unlimited sequence of R5-R2/R3 retries. If hard gates fail, stop with NO-GO.

## Why this is required

Current actions other than COMMIT are inert, observation fully revealed at reset, reference “feedback” is step-based, caller chooses arbitrary action cost, scorer and hidden truth live in same accessible process, frozen M1 dispersion is not constant, empty submission receives utility 0.4 (above 6 of 8 DEV cases), and result schema invalid. The previous nondegenerate FDP range is NOT outcome-grounded sequential scientific decision-making.

## G0: Corrective scientific model and score design, freeze BEFORE new implementation or new DEV outputs

1. Read `planner/reviews/review_005.md`, `research/round_005_d1_mechanism_spec.md`, current D1 code and existing `results/round_005_d1_dev.json`. Preserve them in git history byte-for-byte.
2. Write `research/round_005_r1_d1_corrective_spec.md`, independently critical review plus executable math:
   - Fix M1 as constant `phi_g=phi0` vs M2 variable `phi_g`, or clearly document an alternative mathematical revision and its scientific consequence.
   - Define batch-treatment randomized-within-batch or an explicitly partially confounded but identifiable scheme; require rank AND within-batch overlap/positivity, reject perfect confounding. Detail tested boundary values and protocol confounder effects.
   - Define a **sequential observation acquisition** process. Initially do NOT expose full Y or complete gene summaries. State precisely which samples/genes/QC are visible after actions and what fresh data `ALLOCATE_REPLICATE`, `MEASURE_QC`, `ADD_CONTROL`, `FIT_MODEL` actually provide. If an action cannot be implemented realistically in scope, REMOVE it from legal schema; do not keep fake scientific tools.
   - Define authoritative tool costs (per added sample for allocate), typed validation and actual candidate submission ownership.
   - Define valid discovery-set semantics (unique integer indices, bounds, empty and all-null). Distinguish realized FDP from expected FDR and, if a BH procedure is implemented, describe its p-value assumptions and null calibration; do not claim controlled FDR from realized FDP.
   - Choose a **neutral** utility with a mathematically stated abstain/empty-baseline interpretation. Existing `w1*(1-FDP)` gives empty work +0.4. Fix via versioned model and preserve raw FDP/power/sampling cost; report all weights and tradeoffs independent of strategy names and outcomes. Do NOT tune reward weights merely to favor the proposed feedback policy; negative/zero returns are valid.
   - Specify OS-level candidate/trusted boundary, private task seed and actual loader canary, CRN/noise keyed to sample identity where feasible and honest action-dependent stochasticity limits.
3. **Commit ONLY corrective spec and an independent critical-science review in its own first Git commit**, and record the SHA. This is an engineering semantics freeze, NOT prospective target-trial preregistration. If unable to specify a scientifically meaningful interaction and genuine access boundary, STOP before coding, `NO_GO_D1_MVP`.

## G1: one minimal REAL D1 process, no synthetic no-op tools

1. Modify only `src/scitransfer/simulator/{dgp/bio_expression.py,engine.py,evaluator.py}` and narrow contracts/process helpers if necessary. Favor a minimal scope:
   - `ALLOCATE_REPLICATE` actually adds fresh blinded samples/measurement records with correct batch/treatment, changes aggregate public state, burns **server-side** cost proportional to number of added samples, respects hard sample/action budgets.
   - `MEASURE_QC` returns targeted new QC information with exposure control and explicit cost; `FIT_MODEL` returns a real, documented estimator or remove if absent; `ADD_CONTROL` must add a distinct actual scientific control or be removed. NO accepted action may be inert.
   - `COMMIT_HITS` saves valid **unique bounded** gene IDs in a terminal artifact and separate scorer independently reads it. Reject bool/negative/out-of-range/duplicate IDs, NaN costs, invalid groups/param ranges, extra unused params, negative action cost or caller-forged cost. Prefer server-priced actions with `Action` containing only action type+parameters.
   - After every action, return *only public, newly authorized observations*. No `engine.truth`/private master_seed accessible to candidate, no shared object exposing `HiddenTruth`, and no leaked seeds/stack traces. Candidate interface separated by OS process **plus actual filesystem/access constraints**; both in same unrestricted Python process is FAIL even if named TrustedEvaluator.
   - Make score a pure function of private truth, validated submitted artifact and actual server-measured costs; **no strategy name or tool-action bonus**.
2. Correct DGP spec mismatch and generator input validation: n_genes, n_samples, n_batches, pi0 and assignment overlap; phi M1/M2; numeric finite checks; RNG stream semantics. Use SHA-derived independent **private** keys; display only non-reversible task IDs/hashes candidate-side.
3. A trusted coordinator may hold generator private state, but a hostile candidate process must be unable to open its files/import its live handles. Provide clear process boundary diagram and simulated malicious candidate tests.

## G2: adversarial, causal and statistic correctness tests

MANDATORY assertions with nonzero failure exit. At least:
- A1 budget exploit: `Action.cost=0` or `-1` rejected/no effect; excessive `n_reps` rejected, costs correctly computed; repeated QC cannot gain free data.
- A2 real actions: `ALLOCATE_REPLICATE` changes sample counts, values/information and reset/replay; `MEASURE_QC` exposes only requested subset; invalid actions do not advance/charge; disabled `FIT_MODEL`/control actions fail rather than silently count.
- A3 visible evidence dependence: same legal public decision state, change an actually accessible QC/variance result **alone**, hold step counter/budget/action options constant, verify policy next action changes; show at least one *outcome-relevant* downstream observation/artifact change under a valid intervention. Stop if only prompt text changes.
- A4 terminal submissions: perfect/wrong/empty/all-null/duplicates/out-of-range types, finite and documented utility. Empty no-cost policy must not receive an arbitrary positive “precision” reward. No imposed guarantee that feedback > naive.
- A5 DGP: M1 `phi` constant, M2 gene-specific, within-batch overlap, reject full confounding; expected count/variance sanity, parameter bounds. Empirical checks for null p-value calibration when claiming FDR/BH adjustment.
- A6 trust boundary: run true candidate subprocess through public loader, inject nested canary into hidden truth and scorer inputs, assert canary absent from candidate messages/observations/tool errors/traces/committed artifacts; adversarial candidate cannot access evaluator hidden file or seed.
- A7 strategy identity invariance: vary strategy ID/context while replaying identical validated action/artifact, assert exact evaluator same output; ensure no scorer conditional branches by strategy.
- A8 CPU DEV smoke: >=4 independent DEV tasks across both mechanisms ×2 scripts, plus empty/neutral policies. Compare identical budgets; report actual action-dependent traces, FDP, Power, sample cost and utility. Analyze both policies **without claiming transfer**, and label no-variation honestly. Control discovery-list size or include matching k baseline to distinguish output-cardinality confounding.
- A9 deterministic task replay, action-order/noise paired comparison limitations; negative policy/hidden seed access controls; NO use of leaked historical target seeds 42/43/100/200 as heldout evidence (DEV reuse with explicit label is okay).

## G3: provenance, schema and reporting

- Capture full `python -m pytest tests/ -q -ra` output/return code and targeted test evidence; 129 green from Executor prior report not independent proof of repaired code.
- `results/result_round_005_r1.json` MUST validate against `schemas/result_round.schema.json`: required `environment.benchmark/upstream_ref/official_evaluator_verified`, `runs` (use [] for DEV-only), `tests.command/passed/failed/skipped`, acceptance keys EXACTLY `AC-01..06`; no extra top-level metadata under `additionalProperties:false`. Put R5R1 gate statuses in a separate `results/round_005_r1_gate_audit.md` and quantitative DEV results in `results/round_005_r1_dev.json`. Never mark simulated scores official published benchmark.
- `results/round_005_r1_measurement_audit.md` should document current/previous score exploit, spec hash commit, trusted process+filesystem proof, actual policy trajectories, null calibration, score distributions, and deficiencies. Safe public artifacts only, no gold.
- Keep all Markdown and JSON as plain Git blobs; do not mutate original result history. Update `status.json` and push. Executor cannot mark ACCEPTED.

### Final gates (Planner)

- **R5R1-01:** separate pre-implementation corrective spec commit and proven DGP/evaluator math.
- **R5R1-02:** real sequential acquisition with legal typed and SERVER-priced actions; no inert tool API.
- **R5R1-03:** candidate/trusted OS process/access isolation, dynamic real loader canary and malicious access test.
- **R5R1-04:** correct bounded unique discovery set, FDP/power/empty utility/cost and DGP M1/M2 consistency.
- **R5R1-05:** observed feedback changes decision and downstream task data; DEV performance variable without strategy-ID rewards/cardinality confound.
- **R5R1-06:** full truthful tests, external independent-ish review, schema-valid result, $0 spent, clean Git push.

**HARD STOP:** If any of R5R1-02, -03 or -04 is not feasible without fake measurements or reward hacks, label `NO_GO_D1_MVP`, STOP and seek user/Planner decision. Never auto-start R5-R2 or the D2/D3 implementation.
