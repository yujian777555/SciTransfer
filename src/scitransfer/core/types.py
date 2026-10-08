"""Core typed objects for SciTransfer paired experiments."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional


class Arm(str, Enum):
    NO_STRATEGY = "NO_STRATEGY"
    FIXED_STRATEGY = "FIXED_STRATEGY"
    PLACEBO = "PLACEBO"


class RunStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class Budget:
    """Resource budget for a single run."""

    max_tokens: int = 32_000
    max_cost_usd: float = 1.0
    timeout_s: int = 900

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScientificAction:
    """One step in a research trajectory."""

    step_id: str
    action_type: str  # e.g. "generate_code", "execute", "evaluate"
    content: str
    tool_calls: tuple[str, ...] = ()
    observation: Optional[str] = None
    timestamp_start: Optional[str] = None
    timestamp_end: Optional[str] = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tool_calls"] = list(self.tool_calls)
        return d


@dataclass(frozen=True)
class ScientificStrategy:
    """A domain-agnostic research tactic, NOT a solution hint."""

    strategy_id: str
    preconditions: str
    research_action: str
    expected_evidence: str
    invalidity_conditions: str
    source_provenance: str
    cost_constraints: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def prompt_block(self) -> str:
        """Render as an additive prompt section for arm B."""
        return (
            f"[RESEARCH STRATEGY — {self.strategy_id}]\n"
            f"Preconditions: {self.preconditions}\n"
            f"Recommended research action: {self.research_action}\n"
            f"Expected evidence before claiming success: {self.expected_evidence}\n"
            f"Invalid when: {self.invalidity_conditions}\n"
            f"Cost constraint: {self.cost_constraints or 'none specified'}\n"
            f"Provenance: {self.source_provenance}\n"
            "[END STRATEGY]"
        )


@dataclass(frozen=True)
class ResearchState:
    """Snapshot of agent state at a point in the trajectory."""

    task_id: str
    domain: str
    arm: Arm
    seed: int
    agent_id: str
    agent_model: str
    environment_sha: str
    prompt_hash: str
    strategy_hash: Optional[str] = None
    budget: Budget = field(default_factory=Budget)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["arm"] = self.arm.value
        d["budget"] = self.budget.to_dict()
        return d


@dataclass
class StepRecord:
    """Append-only per-action trace record."""

    task_id: str
    domain: str
    arm: str
    seed: int
    agent_id: str
    agent_model: str
    environment_sha: str
    prompt_hash: str
    strategy_id: Optional[str]
    strategy_hash: Optional[str]
    step_id: str
    action_type: str
    content: str
    tool_calls: list[str]
    observation: Optional[str]
    timestamp_start: str
    timestamp_end: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    status: str
    exit_reason: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunResult:
    """Final result of one arm on one task."""

    task_id: str
    domain: str
    arm: str
    seed: int
    agent_id: str
    agent_model: str
    status: str
    score: Optional[float]
    official_evaluation: bool
    cost_usd: Optional[float]
    tokens_in: int
    tokens_out: int
    prompt_hash: str
    strategy_id: Optional[str]
    strategy_hash: Optional[str]
    environment_sha: str
    trace_path: Optional[str]
    evaluator_output_path: Optional[str]
    error: Optional[str]
    exit_reason: Optional[str]
    started_at: str
    finished_at: str
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
