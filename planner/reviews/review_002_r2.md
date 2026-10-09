# SciTransfer — Planner Review of Round 002-R2 (2026-10-09)

**Executor HEAD reviewed:** `b05c446162c65e129185e20936b514c93ab552f6`  
**Outcome:** **NOT ACCEPTED as a preregistered, reproducible strategy A/B evaluation.**  
**Decision:** Close Phase0-B at **NO-GO for the CURRENT DiscoveryWorld + DeepSeek pilot configuration**, NOT no-go for scientific strategy transfer as a research hypothesis. Phase1 training and any further paid benchmark sweep are UNAUTHORIZED.
**Next:** `planner/plan_003.md` (Phase0-C, one bounded *offline* alternative-benchmark and measurement-validity gate).

## Evidence provenance

Planner read the current public GitHub commit, pre-registration file, scripts `r2_llm_pilot.py` and `r2_llm_pilot_v2.py`, reported results, preflight, canary tests, and project charter. Planner also looked at `CMarsRover/SciAgentGYM` README as an alternative candidate. No access to the executor's secrets, local raw API HTTP bodies, full test output, or private runtime; reported four episodes and 114 green tests cannot be independently reproduced from GitHub. Do not accuse the executor of fabricated calls; the required audit evidence is simply missing.

## What can be credited

- Public tracked `*_trusted.json` files were untracked in the R2 commit; `.gitignore` includes appropriate future filters. **Historical** leak remains retrievable in Git history. Old exposed seeds 42/43/100 must stay quarantined.
- Two existing DiscoveryWorld scenarios and both arms were attempted per Executor, the resulting JSON records 4 entries and zero reward deltas. Registered strategy remains hand-authored, not learned or transferred.
- `src/scitransfer/secure_input.py` provides a recursive hidden-key filter and canary unit tests. These tests are useful for a potential candidate-facing bridge, but neither actual LLM runner imports/calls `build_model_input()`.
- The executor reports API cost `0.073729` USD and 114 passing tests. Cost is a **local usage-based estimate**, not an authenticated provider bill; no raw usage or full pytest log is committed.

## P0 — preregistration timing and immutability unproven (actually contradictory)

- `experiments/round_002_r2_preregistration.json` first appears in the **same final commit** `b05c446162c65e129185e20936b514c93ab552f6` as the result artifacts. No separate pre-run registered Git commit exists on `main`.
- Its `timestamp_utc` is **2026-10-09T22:00:00Z**, whereas the FINAL commit's Git author and committer timestamp is **2026-10-09T13:42:28Z**. This declared registration timestamp is **over eight hours AFTER the recorded final commit**, so it cannot establish prospective registration.
- `scripts/r2_g1_diagnostic.py` pretests **Combinatorial Chemistry seed 200** and the target pilot reuses **the same seed 200**. This seed is not a genuinely held-out target for that scenario.
- A preregistration written retrospectively cannot be fixed by changing its date. Preserve original and mark `PREREG_UNVERIFIED / CONTAMINATED`.

## P0 — executed configuration diverges from filed preregistration

- File registers a strategy paragraph about **writing/loading data and iterative code output**, unsuitable to direct interactive DiscoveryWorld actions. This is not a task-aligned conditional experimental decision policy.
- `r2_llm_pilot_v2.py` uses **a shortened DIFFERENT strategy paragraph** and `max_tokens=1024`, versus registered strategy and `max_tokens_per_call=2048`. v2 uses **10** steps versus registered limit **15**; even if maxima are bounds, the actual treatment hash/configuration must be recorded. Fixed baseline-before-strategy arm ordering is not the stated randomized order.
- `r2_llm_pilot_v2.py` bypasses `build_model_input()`; both scripts call `get_safe_task_description()` but no dynamic model-message canary or enforced common vetted bridge is demonstrated. Local source filter tests do not certify the real model request payloads.
- Invalid/non-JSON LLM responses silently fall back to `MOVE_DIRECTION east`, concealing model/action parsing failures and potentially inflating plausible movements. API errors in `call_llm()` are returned as content instead of triggering fail-closed. This makes action validity and even provider-call success unverifiable from summary counts alone.
- Budget stop logic tests `existing.total_cost_usd > 1.0` only **before each episode**, not before every API request/response; it cannot guarantee a hard cumulative spend ceiling. Pricing is guessed from fixed coefficients rather than verified provider billing. Do not claim strict budget enforcement.

## P0 — missing authentic episode-level evidence

Only `results/round_002_r2_pilot/r2_llm_pilot_results.json` is tracked. It includes 4 summary objects, not stepwise model/tool/observation traces, per-call HTTP metadata, token counts, reported usage, version, timestamps, action parsing errors, or score provenance. Neither runner saves redacted full request/response logs. Consequently `R2R2-03`, `R2R2-04`, `R2R2-05`, and `R2R2-06` cannot be certified simply from the report.

`results/round_002_r2_preflight.md` still contains the literal **`[to be filled after full run]`** where the mandatory full-suite pytest outcome should be, despite G2 being marked PASS. The JSON states 114 tests passed, but no complete original command output is committed.

## P1 — scientific construct still untested

- `scripts/r2_g1_diagnostic.py` attributes scientific achievement to merely `PICKUP rusted key`, which may earn task subscore +1 but is **inventory acquisition**, not experimental observation / hypothesis testing. Need distinguish navigation/collection/instrument use and measured scientific inference.
- All four reported score deltas are 0. Thus no signal of evaluated outcome benefit under this configuration, with only 2 scenarios × 1 paired seed each. This is a failed feasibility demonstration, **not evidence the cross-domain strategy transfer hypothesis is false**.
- The arms compare a prompt about writing code in a game-like tool-use environment; even a valid paired outcome would not test a strategy **learned in a source scientific domain and transferred to a target**.

## Gate assessment

| Gate | Planner verdict |
|---|---|
| R2R2-01 | PARTIAL: current tracked trusted files removed; historical exposure persists; live model-input canary not demonstrated |
| R2R2-02 | PARTIAL: source demonstrates legal actions/score from key pickup, but no observed experimental reasoning |
| R2R2-03 | **FAIL**: no verifiable preregistration, configuration mismatch, contaminated target seed |
| R2R2-04 | REPORTED ONLY: 114 passing tests claimed, preflight log placeholder |
| R2R2-05 | **NOT VERIFIED**: 4 result summaries exist, but no per-step replayable model/API action traces |
| R2R2-06 | REPORTED <=$1, **NOT AUDITABLE**: usage-based estimate only, no hard per-request cost gate |
| R2R2-07 | PASS: no learned-transfer / statistical significance claim |
| R2R2-08 | Git push verified; **scientific acceptance denied** |

## Planner scientific decision

**Close Phase0-B / Round002 as INCONCLUSIVE / MEASUREMENT_INVALID FOR TRANSFER.** The completed implementation gives useful engineering lessons but no publishable A/B transfer result. **Stop DiscoveryWorld paid retries under current setup. Do not train a predictor, utility gate or learned controller.**

**Next bounded task:** Phase0-C / Round003 `planner/plan_003.md`. One offline, timeboxed (2h installation, 0 paid API) audit of *SciAgentGYM* multi-step scientific tools and verifiers, with ScienceAgentBench and DiscoveryWorld as reference comparators. Test reproducibility, action/scorer validity, source/target domain disjointness and hidden answer isolation; deliver GO/NO-GO without promising it works or silently changing the charter's research question. If none fits, stop and propose a **method-level** redesign rather than another paid sweep.
