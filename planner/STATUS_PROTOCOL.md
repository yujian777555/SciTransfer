# Planner–Executor status contract

Branch `main` plus Git commit history is the only source of truth.

## State machine

- `AWAITING_EXECUTOR`: Planner issued a plan; Executor has not submitted evidence.
- `IN_PROGRESS`: Executor has started implementation (not accepted).
- `AWAITING_PLANNER_REVIEW`: Executor submitted deliverables and results; Planner must inspect them.
- `PARTIAL`: Some requested work done, hard acceptance outstanding.
- `BLOCKED`: Further execution requires an external decision/resource.
- `ACCEPTED`: Planner-reviewed complete evidence and accepted the round (Planner action only).
- `REPLAN_REQUIRED`: Planner found invalid or insufficient evidence and will issue remediation.

Executor updates `status.json` to `IN_PROGRESS`, `PARTIAL`, `BLOCKED`, or `AWAITING_PLANNER_REVIEW` together with actual paths/commits and result file. Executor cannot set ACCEPTED. Planner reviews exact implementation commit, test and evaluator artifacts and writes next plan/review.

`current_round` is an integer, starting at 1. `latest_plan` and `latest_result` are repo-relative paths; null means not yet submitted. `base_commit_at_planning` records the known head **before** the Planner issued this commit, not the resulting planner commit. On update, preserve unknown fields unless conflicting.

## Round result JSON

Must validate against `schemas/result_round.schema.json`. Use null for unknown quantities, not zero. `official_evaluation` is true only when upstream evaluator actually ran; recorded failure scores must not be replaced with guessed values. Tests summary is required even for BLOCKED status. Record artifact paths and checksums where feasible.

Do not invent commit SHAs to satisfy circular references; the response message can report final pushed HEAD independently of an in-commit `implementation_commit` field.
