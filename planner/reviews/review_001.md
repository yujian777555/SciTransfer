# Planner Review — Round 001 (2026-10-08)

**Repository:** https://github.com/yujian777555/SciTransfer  
**Reviewed executor commit:** `9417ae767cda079db7c170c5f3054325d7608cb4`  
**Planner verdict:** **NOT ACCEPTED / REMEDIATION REQUIRED**  
**Next plan:** `planner/plan_001_r1.md` (Round 001-R1, not Round 002)  
**Evidence basis:** GitHub source, stored result/trace metadata, six generated code artifacts and upstream ScienceAgentBench evaluation source at commit `c26e151ed601ba109dc4d35e057ff8e73fec469d`. **No local re-execution of the 24 tests and no official benchmark scores were obtained by Planner.**

## 1. Confirmed progress

1. `main` HEAD equals submitted SHA `9417ae767cda079db7c170c5f3054325d7608cb4`; `status.json` is PARTIAL and points at `results/result_round_001.json`.
2. 102-row verified parquet and manifest are committed with file-level hash; 3 selected tasks span Bioinformatics (#85), Computational Chemistry (#16), and GIS (#21).
3. Six DeepSeek code-generation calls were recorded (3 tasks × 2 arms × seed 0), including prompts, generated Python programs, tokens, estimated costs, traces and a summary. These are **code generation runs**, not 6 executed scientific experiments.
4. Result JSON explicitly reports zero official evaluation results; all six `official_evaluation:false`, `score:null`, status BLOCKED. No evidence of fabricated scores.
5. Tests file includes 24 safeguard test functions and executor reports 24 passed / 0 failed / 0 skipped; the Planner **has not independently rerun** them.
6. Reported API cost: USD 0.047211 estimated (not independently verified provider invoice); published output/input pricing in result is merely estimate.

## 2. Acceptance matrix

| ID | Verdict | Explanation |
|---|---|---|
| AC-01 | CONDITIONAL / INCOMPLETE | Dataset provenance largely recorded. Upstream evaluator inspected, but not actually executable or validated. |
| AC-02 | BLOCKED | Three domains chosen; zero actual official scores. |
| AC-03 | BLOCKED | Three A/B **generation** pairs recorded; zero A/B pairs evaluated by official harness. |
| AC-04 | PARTIAL | Strong logging foundation; benchmark/runtime path inconsistency, log parsing risk, and preregistration timestamp conflict undermine full reproducibility. |
| AC-05 | REPORTED PASS / UNVERIFIED | 24/24 pytest claimed and tests present; no independent runtime execution by Planner. Critical integration tests absent. |
| AC-06 | PUSH VERIFIED / ROUND NOT ACCEPTED | HEAD and status handoff confirmed; full research round remains NOT ACCEPTED. |

## 3. Blocking implementation defects — inspect and fix before trusting any score

**P0: Wrong dataset split.** `src/scitransfer/benchmarks/scienceagentbench.py` constructs official evaluator command without `--split verified`. Pinned upstream harness defaults to `validation`. A future evaluation can silently score the wrong dataset version, despite the local verified parquet being selected.

**P0: Wrong score association.** Current parser takes the *first* JSONL entry containing score fields. Upstream `run_evaluation.py` writes one output line for **each dataset row**, with placeholder scores for unevaluated rows and no instance_id in those JSONL lines. Current parser can attribute a different instance's or placeholder score to task 85/16/21. Must resolve unique row index for the **same pinned verified split**, validate expected row count and target row, verify target was actually run, and refuse any ambiguity. Upstream's `examples_to_run` log plus row-index mapping should be preserved.

**P0: Relative-path / working-directory mismatch.** `run_official_evaluation` invokes a subprocess with `cwd=upstream_dir`, but supplies relative `benchmark_dir`, `pred_program_path` and `log_fname`; the readiness defaults point to a `benchmarks/ScienceAgentBench-upstream` location inconsistent with the audit's `../ScienceAgentBench-upstream`. Normalize and verify absolute paths with a single configurable source.

**P0: Incorrect official-success flag.** The wrapper currently returns `official_evaluation=True` after a zero exit code even if `success_rate` was never parsed, and may accept score fields without proving they correspond to the requested task. Must fail closed on empty/missing/mismatched/partial evaluator results.

**P0: Harness platform and API preflight.** Pinned upstream imports Unix `resource`; native Windows Python import is not a reliable executable route. Upstream harness also checks `OPENAI_API_KEY` / Azure credentials at startup *before* per-task assessment even if selected outputs are non-visual. The earlier claim that three nonvisual tasks definitely need no OpenAI credential is not established. Validate official behavior under WSL2/Linux and approved credentials. Do not invent an API key, change its semantics silently, or label a patched evaluator 'unmodified official'.

**P1: Claimed strategy preregistration lacks timestamp evidence.** `experiments/round_001_config.json` contains `preregistered_at=2026-10-08T22:00:00Z`, but recorded runs start ~2026-10-08T14:44–14:50Z, about seven hours *earlier*. Likely a timezone error; cannot verify preregistration from that field. Preserve original; report ambiguity and create a prospective hash-stamped immutable registration before any future outcomes. Do not retroactively backdate.

**P1: Strategy construct mismatch.** `FIXED_STRATEGY` instructs 'baseline → execute → observe → iteratively rerun'; actual `scitransfer-direct-prompt` code has **one model call**, no iterative execution, tools or feedback. A/B arms currently test *prompt conditioning for code generation*, not adaptive scientific decision policies. Official scores will establish only a smoke test of this limited intervention; genuine research-policy transfer requires an executable multi-action harness later.

**P1: Destructive downloader startup / resume proof.** `scripts/start_download.ps1` deletes `benchmark_verified.zip` before starting, risking loss of ~26% download. The Python downloader does not comprehensively verify resumed `Content-Range` starting offset or ensure final zip integrity before reporting DONE. Two `ChildProcess.kill` messages indicate wrapper/process control failure, NOT evidence that a downloader is safely running. Correct resume and inspection flow before restarting.

**P1: Agent sandbox allowlist.** Error `Access denied - path outside allowed directories: C:\\Users\\于舰\\XiaomiMiMoProjects\\SciTransfer` is a tool sandbox/path authorization issue, not a GitHub permission issue. Relocate / re-clone inside allowed Documents or Desktop folder, or obtain authorized access adjustment; do not attempt to bypass constraints.

**P2: Seed reproducibility.** Recorded `seed=0` identifies pairing, but direct model request only sets temperature=0 and does not pass a model seed. Thus zero is not proof of deterministic paired stochastic sampling; report honest model stochasticity and replicate later.

## 4. Scientific inference boundary

Current data support: a reproducible attempt at *single-shot* paired strategy prompting and environment provenance. They **do not** support: real benchmark performance, causal impact of a scientific decision strategy, cross-domain transfer, statistical significance, or trained policy utility.

## 5. Decision

Issue **Round 001-R1 targeted remediation** on the same `current_round=1`. Executor must repair official evaluator correctness, artifact retrieval and test coverage, then obtain three genuine evaluated A/B pairs (or return BLOCKED with verifiable causes). Do not run broad experiments or start training. Preserve all historical Round 001 artifacts unmodified.

Planner to review again after Executor pushes `results/result_round_001_r1.json` and updates `status.json`.
