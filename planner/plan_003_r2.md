# SciTransfer Round 003-R2 — Final Native Toolkit Evidence Gate (No New Research Scope)

**Issued:** 2026-10-09
**Planner:** ChatGPT; **Executor:** Kimi/MiMo
**Repo:** https://github.com/yujian777555/SciTransfer (`main`)
**Exact audited Executor HEAD:** `672b17f13d5811b717cd320dda1a51720af076d1`
**Formal review:** `planner/reviews/review_003_r1.md`
**SciAgentGYM upstream PIN:** `e9dbbea4369d67694e38bf8be67bedbcaf9e9300`
**State:** PHASE0-C / Round003-R2; NOT Phase1.
**Budget:** $0 API, no training, no new scientific target episodes; **HARD 60-minute timebox**.
**Purpose:** one **last** end-to-end authentic upstream tool and scoring proof, NOT another infrastructure program.

## Why

The prior sequential physics tool calls and chemistry molecular-weight example were both implemented as local `GenericFunctionTool` closures despite importing upstream toolkit modules. The 1800nm intermediate value had a hardcoded fallback. Canary tested a manually constructed candidate view, not a real loader. The scorer's mismatch branch invokes LLM. Current `status.json`, R1 result and reports are Git LFS pointer blobs, so Planner couldn't read their purported evidence. Treat R1 as PARTIAL and correct only those exact defects.

## Step 0 — Restore Git control-plane inspectability (MANDATORY, first)

1. Pull `main` fast-forward, verify HEAD and worktree. Check `git check-attr -a -- status.json planner/latest_plan.md results/result_round_003_r1.json`. Existing `.gitattributes` must **not** route all `*.json`/`*.md` through LFS. Planner will replace it with `*.json text -filter` and `*.md text -filter`.
2. For the FOUR LFS pointer files: `status.json`, `results/result_round_003_r1.json`, `benchmarks/round_003_r1_sciagentgym_runtime.md`, `results/round_003_r1_scorer_integrity.md`, recover **actual original contents** from the Executor's local working copies or `git lfs pull`; re-add as normal Git blobs in a **new** non-force commit. Preserve prior pointer OIDs/SHA and text checksums in a short erratum; never invent missing report content. Do not `git add --renormalize .` for the entire repo.
3. Verify `git show HEAD:status.json` starts with `{`, and `git show HEAD:...md` starts with Markdown, not `version https://git-lfs...`. Verify using remote GitHub fetch after push. If not recoverable, mark original R1 evidence unavailable; still keep Planner state as ordinary Git text.
4. Keep any Git-tracked gold/answer material out of repo; no pushes of hidden data/private paths. Do not modify historical 001/002/003 score contents.

## Step 1 — Verify original installed source and native science tools

1. Prove LOCAL checkout with `git -C <checkout> rev-parse HEAD` exactly `e9dbbea4369d67694e38bf8be67bedbcaf9e9300`, path/checksum manifest for imported `gym/env.py`, `gym/core/evaluator.py`, `gym/core/tool_loader.py`, and selected native toolkit files; verify no local modifications to those upstream files. Capture versions, sanitized stdout/stderr and exit codes.
2. **Do NOT define new GenericFunctionTool, wrap custom functions, hardcode numerical results, or silently fall back.** Resolve a real `Toolbox.get_tool` or `prepare_env_from_query` registered upstream tool and execute it through `MinimalSciEnv/ToolCall` or official harness. Cite source toolkit file/class/function and commit SHA.
3. Use one small real DEV task in physics: native tool A produces real output; then use that output to make a genuine follow-up decision selecting/parameterizing an **upstream native** tool B. Require actual nonempty original observation, strict parsing, no 1800/default, assertions on argument derivation and tool outputs; failure => nonzero process exit.
4. Run one real **upstream** chemistry tool in separate task using actual toolkit class/registered function; do NOT substitute manually defined molecular-weight lookup. Verify output from tool, including source function identity.
5. If a native tool B does not exist, or only framework-dispatch mock calls can be made: STOP and report `NO_GO_NATIVE_TOOL_VALIDITY`.

## Step 2 — Real candidate/trusted split and scorer decision

1. Use one genuine pinned SciAgentGYM DEV case and native `prepare_env_from_query` or documented equivalent loader; build candidate view by **allowlisting** question, permitted tool schemas, public observations. Explicitly deny `answer`, `golden_answer`, `solution_steps`, `tool_expected`, `refined_versions[*].final_answer`; protect scorer/hidden dataset in separate trust scope. Dynamically inject nested canary through the **actual loader-to-candidate** path and test model-ready payload, agent traces and Git-staged files for leaks. Synthetic dict-only canary cannot satisfy gate.
2. With zero paid API, run perfect/mismatched/missing/near-correct DEV answers into pinned scorer under active network/judge deny guard. `calculate_answer_score` can invoke `secondary_verification_with_llm` on mismatches; when triggered, return `JUDGE_REQUIRED` with score `null` (do not replace with fabricated offline 'official' 0). Report exact original scorer/observed fallback and scope of deterministic offline subset.
3. No official scored target task, LLM request, leaked answer in repo, or experimental success claim. Runtime smoke only.

## Step 3 — Tests and immutable evidence

1. Convert 'test scripts' to tests with **assertions and nonzero failure exit**, no broad `except: print FAIL; continue`. Capture actual commands/return codes, full selected tests incl. old 114 only if rerun, pass/fail/skip and runtime.
2. Save `results/round_003_r2_native_tool_trace.json` with sanitized two-step input-output, genuine native tool source hash, error handling and dependence proof; separate minimal chemistry trace with legal source, no gold.
3. Save `results/round_003_r2_integrity.md` with recovered LFS OIDs + metadata, upstream checkout rev, candidate/trusted canary test, scorer judge-denial matrix and limits. Keep private judge/gold full data local ONLY.
4. `results/result_round_003_r2.json` and updated plain-Git `status.json` with exact gate verdicts; commit+push main and report final SHA + clean tree status. No `ACCEPTED` by Executor.

### Hard acceptance gates

- **R3R2-01:** text Git integrity restored; actual R1 artifact content recovered or explicitly unavailable.
- **R3R2-02:** exact pinned upstream source proven in local runtime.
- **R3R2-03:** **TWO real upstream scientific-tool calls**, output of first verified and used in second with no default; asserted and logged.
- **R3R2-04:** one independent **native** second-discipline tool run.
- **R3R2-05:** nested canary against real task loader→candidate path; hidden answers absent in all exported artifacts.
- **R3R2-06:** authentic scorer with judge-denial, truthful null/JUDGE_REQUIRED; no unverified 0 scores.
- **R3R2-07:** actual assertions, exit codes and honest all-test count plus $0 spend.
- **R3R2-08:** safe commits, planner review pending, truthful GO / NO-GO.

**Hard STOP:** Any inability to restore safe data, run two native tools, or maintain hidden boundary within 60 minutes means `NO_GO_FOR_SCIAGENTGYM` / `BLOCKED`. Do NOT do R3-R3/R4, train Phase1, or run paid APIs. Return results and wait for the user's decision to authorize a **new controlled multi-domain research simulator** if desirable.
