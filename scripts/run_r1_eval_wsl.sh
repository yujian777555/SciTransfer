#!/bin/bash
# R1: Run official ScienceAgentBench evaluation under WSL Ubuntu-22.04.
# This script must be run INSIDE WSL: wsl -d Ubuntu-22.04 -- bash /path/to/this/script.sh
#
# Usage: bash run_r1_eval_wsl.sh
#
# Prerequisites:
#   1. benchmark_verified.zip extracted to benchmarks/ScienceAgentBench/benchmark/
#   2. Docker accessible (sg docker or docker group membership)
#   3. OPENAI_API_KEY set (upstream harness preflight; non-empty check only)
#   4. Upstream code at benchmarks/ScienceAgentBench-upstream/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
UPSTREAM_DIR="$REPO_DIR/benchmarks/ScienceAgentBench-upstream"
BENCHMARK_DIR="$REPO_DIR/benchmarks/ScienceAgentBench/benchmark"
RESULTS_DIR="$REPO_DIR/results/round_001_r1_runs"

echo "=== R1 Evaluator Smoke Test ==="
echo "Upstream: $UPSTREAM_DIR"
echo "Benchmark: $BENCHMARK_DIR"
echo "Results: $RESULTS_DIR"

# Verify artifacts
if [ ! -d "$BENCHMARK_DIR/eval_programs" ]; then
    echo "BLOCKED: $BENCHMARK_DIR/eval_programs not found. Extract benchmark_verified.zip first."
    exit 1
fi

# Verify resource module
python3 -c "import resource; print('resource OK')"

# Verify Docker
if ! docker ps &>/dev/null; then
    echo "BLOCKED: Docker not accessible. Run with: sg docker -c 'bash $0'"
    exit 1
fi

# Credential preflight (upstream requires non-empty OPENAI_API_KEY or Azure)
if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "BLOCKED: OPENAI_API_KEY not set. Upstream harness requires it."
    echo "Set a valid key: export OPENAI_API_KEY=sk-..."
    exit 1
fi
echo "OPENAI_API_KEY is set (length: ${#OPENAI_API_KEY})"

# Run evaluation for instance 85 (smoke test)
INSTANCE_ID=85
RUN_ID="r1_smoke_i${INSTANCE_ID}"
GOLD_NAME="saliva.py"
PRED_DIR="$RESULTS_DIR/sab_verified_85__NO_STRATEGY__seed0__eval/pred_programs"
LOG_FNAME="$RESULTS_DIR/r1_smoke_i${INSTANCE_ID}_eval.jsonl"

echo ""
echo "=== Evaluating instance $INSTANCE_ID (smoke) ==="
echo "  pred_program_path: $PRED_DIR"
echo "  log_fname: $LOG_FNAME"
echo "  run_id: $RUN_ID"
echo "  split: verified"

cd "$UPSTREAM_DIR"
export PYTHONPATH="$UPSTREAM_DIR:${PYTHONPATH:-}"

python3 -m evaluation.harness.run_evaluation \
    --benchmark_path "$BENCHMARK_DIR" \
    --pred_program_path "$PRED_DIR" \
    --log_fname "$LOG_FNAME" \
    --run_id "$RUN_ID" \
    --split verified \
    --cache_level base \
    --max_workers 1 \
    --instance_ids "$INSTANCE_ID"

echo ""
echo "=== Smoke test complete ==="
echo "Check results at: $LOG_FNAME"
echo "Check evidence at: $UPSTREAM_DIR/logs/run_evaluation/$RUN_ID/$INSTANCE_ID/output/result.json"
