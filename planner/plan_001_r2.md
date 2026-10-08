# Planner Plan — Round 001-R2: Verified Artifact Recovery and Evaluator Closure

Issued 2026-10-09 | Planner ChatGPT | Executor Kimi/MiMo
Repo: https://github.com/yujian777555/SciTransfer
Base: 1610145e04634fafe2f25447eba0ef39e5d839b3
Review: planner/reviews/review_001_r1.md
Branch: main | Phase: 0 | Round: 001-R2 (NOT 002)

## Objective / non-goals

Obtain trustworthy official evaluator results for the SIX EXISTING Round 001 code programs (task 85,16,21; each A/B). If blocked, produce a precise auditable blocker and user action. NO fresh model generation, no expanded benchmarks, no model training, no paper claims, no changed scientific direction. Keep all Round 001 and R1 original data byte-for-byte unchanged; write only new R2 evidence in results/round_001_r2_runs and a new R2 result JSON.

## Step 0: Safety and provenance preflight

1. git pull --ff-only, git status, read status.json, latest_plan, review_001_r1.md, result_round_001_r1.json and six SHA256 catalog entries. Report current HEAD and exact accessible workspace.
2. File access errors outside allowed Documents/Desktop paths require an authorized relocated checkout or explicit permission; do NOT bypass tool security. Do not assume ChildProcess.kill means background process survived.
3. Record a fresh timestamped measurement of ZIP path, byte length, download PID, whether size grows, stdout/stderr last lines, Docker daemon, WSL version and Python dependency imports. Previous contradictory snapshots are historical, not current truth.
4. Never expose API tokens, proprietary raw datasets or unzipped protected benchmark files in Git, logs or chat.

## Step 1: Fix download robustness BEFORE resuming

1. Only ONE process can write the partial ZIP. Acquire exclusive process lock; refuse concurrent writer; preserve partial bytes and corrupted prior attempt evidence.
2. For any HTTP 206 response, require valid Content-Range matching requested start byte and expected end/total; reject and CLOSE mismatched/missing ranges WITHOUT writing their body. On HTTP 200 to a resume request, start a NEW staged full-file download safely (not truncate existing partial until verified). Handle 416 by inspecting full-file validity; never silently append.
3. Detect premature EOF, response length mismatch, retry exhaustion, timeout, network denial and process termination. Use staged .part file and atomic finish only after expected exact byte length 1769478786, ZIP directory test, encrypted extraction test, and full SHA256. A computed SHA on incomplete/corrupted ZIP does NOT prove completeness.
4. Provide automated local mock-response tests: valid 206, wrong offset, absent Content-Range, 200 ignoring Range, 416, truncated response, duplicate writer, good final ZIP, bad ZIP. Run real tests; report pass/fail/skip.
5. Do not repeatedly start unmonitored downloads. If SharePoint remains inaccessible/slow or process tool kills it, stop after bounded attempts and report a single user-safe recovery: user downloads benchmark_verified.zip from the official ScienceAgentBench README link via browser and places it in authorized local artifacts directory. Never invent alternative download sources or redistribute the unzipped files.

## Step 2: Run unmodified evaluator in a REAL supported environment

1. Prefer WSL2 Ubuntu/Linux Python, working Docker daemon with image build network and pinned upstream ScienceAgentBench commit c26e151ed601ba109dc4d35e057ff8e73fec469d. Native Windows resource shim may be tested as DISLOSED modified compatibility mode only; not a substitute for a confirmed official Linux run.
2. Fix evaluator paths/config so upstream source, benchmark archive tree, predictions and output log resolve to absolute paths. scripts/run_r1_eval_wsl.sh must prepare/check its prediction directory BEFORE invoking upstream CLI.
3. Verify both task loader and upstream load_dataset(..., split=verified) see identical pinned HF dataset revision 9c6e96c9e74572e979b0930ee735041cef528cb7, or read a pinned local identical dataset with clearly disclosed adapter if upstream cannot accept revision. Compare all 102 ordered task IDs; on mismatch STOP with null scores.
4. Valid OpenAI/Azure credentials: upstream preflight checks even for nonvisual tasks; do not treat DashScope key as genuine OpenAI key or use a fake string. If an unmodified upstream execution requires valid credentials, ask user to configure them locally (never in chat/Git). If nonvisual-only fork is needed, disclose diff and label results MODIFIED-EVALUATOR with validation; do not claim unmodified official provenance.
5. scripts/r1_evaluate_existing.py must confirm each stored program SHA256 matches results/round_001_r1_program_hashes.json BEFORE copying/launching; do not regenerate programs.
6. For each run, use fresh unique run ID and separate output/log directory. Delete/reject only stale files within fresh R2-specific temp paths, never prior results. Bind task instance ID, candidate program hash, official log row index, output execution evidence run ID/content and evaluator version. Existence of any result.json alone is insufficient evidence of current execution.

## Step 3: Smoke then six scores

1. Smoke FIRST: Task85 NO_STRATEGY existing program. Run supported evaluator, require real execution evidence + correct 102-row JSONL index + score + raw stdout/stderr. A real evaluated failure score=0 is valid if all provenance passes.
2. Only then evaluate the remaining 5 previously generated programs for #85 B, #16 A/B, #21 A/B. Record separate run IDs, full scores, raw official logs, program hashes, wall time, actual cost and Docker details. No new DeepSeek calls.
3. Summarize per-pair B-A score ONLY when both arms have valid genuine evaluation. Zero completed pairs means zero scientific performance claims.
4. If Docker, ZIP, HF dataset or legal credentials remain blockers: STOP, do not label a score official, report BLOCKED/PARTIAL, exact command/stdout/stderr/bytes/paths and minimal user intervention.

## Step 4: Tests, reports, handoff

- Rerun all 43 baseline tests and R2 additions with explicit command and pass/fail/skip counts. Add tests for 206 mismatch discard, absent range, fake/stale result.json, HF row-order mismatch, missing pred dir, source hash mismatch, evaluator nonzero return and valid score zero.
- Preserve preregistration status UNVERIFIED, seed=0 as pair label, and description as retrospective single-shot strategy-prompt ablation.
- New deliverables: results/round_001_r2_preflight.md; results/round_001_r2_evaluation_matrix.csv; results/round_001_r2_runs/; results/result_round_001_r2.json; any code/tests fixes; status.json. Retain original 001 and R1 raw results unchanged.
- Do not put full official benchmark datasets or proprietary artifacts into Git.

## R2 gates

R2-01: Safe single-writer downloader tested; full ZIP verified OR explicit BLOCKED.
R2-02: Verified split revision and ordered task mapping identical in evaluator; paths and predictions proven.
R2-03: Unmodified Linux/WSL evaluation actually executed, or clearly labeled modified evaluator assessed separately; credentials safe.
R2-04: No cross-task/filler/stale score attribution; exact program hashes and real run-specific evidence.
R2-05: Six authentic evaluations, 3 A/B pairs, else PARTIAL/BLOCKED (not accepted).
R2-06: Original 43 tests plus new tests pass; exact totals recorded (never fictitious).
R2-07: Historical data unchanged; no new LLM generation/backdated preregistration/overstated scientific claim.
R2-08: Deliverables pushed to main, status AWAITING_PLANNER_REVIEW, PARTIAL or BLOCKED, Planner alone decides ACCEPTED.

## Stop and handoff

If download/download permissions or credentials remain unavailable, do not endlessly restart. Report actionable BLOCKED state. If manual action is required, state the official download URL, byte size, target authorized folder and one verification command; avoid requesting credentials in chat.

Report exact final commit SHA, actual ZIP size/hash/validation, WSL/Docker status, Task85 smoke outcome, 6 per-program results with row indexes and run IDs, tests, R2-01..08, unresolved blocker evidence and estimated next cost. No Round 002 without Planner acceptance.
