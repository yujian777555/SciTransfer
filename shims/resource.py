"""Windows compatibility shim for the Unix-only `resource` module.

**DISCLOSED ADAPTATION — NOT unmodified official evaluator.**

The upstream ScienceAgentBench harness (`evaluation/harness/run_evaluation.py`)
imports `resource` (Unix-only) and calls `resource.setrlimit(resource.RLIMIT_NOFILE, ...)`.
On Windows this module does not exist.

This shim provides the minimal API surface used by the upstream harness so it
can run on Windows Python. The actual resource limit call is a no-op on Windows.

Usage: prepend this directory to PYTHONPATH before running the harness:
    set PYTHONPATH=C:\path\to\shims;C:\path\to\ScienceAgentBench-upstream

This is a **platform compatibility adaptation**, not a modification to
evaluation logic. All scoring, Docker execution, and JSONL output are
identical to the unmodified upstream harness.
"""
import os
import sys

# Constants used by the upstream harness
RLIMIT_NOFILE = 7  # POSIX value


def getrlimit(resource_type):
    """Return (soft, hard) limit. On Windows, return a permissive default."""
    return (4096, 4096)


def setrlimit(resource_type, limits):
    """Set resource limit. On Windows, this is a no-op (documented adaptation)."""
    # Windows does not support setrlimit. The upstream harness calls this to
    # raise the open-file limit for parallel Docker operations. On Windows,
    # the OS manages file handles differently.
    pass


# Ensure this shim is importable as 'resource'
if __name__ != "resource":
    pass
