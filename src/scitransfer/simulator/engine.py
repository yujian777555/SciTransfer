"""D1 Experiment Engine: sequential action-observation loop."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np

from .dgp.bio_expression import (
    D1TaskConfig,
    HiddenTruth,
    PublicObservation,
    generate_task,
    get_public_observation,
)


@dataclass
class Action:
    """Typed action with validation."""
    action_type: str
    parameters: dict
    cost: int


@dataclass
class StepResult:
    """Result of one step."""
    observation: PublicObservation
    reward: float
    done: bool
    info: dict
    error: Optional[str] = None


VALID_ACTIONS = {
    "ALLOCATE_REPLICATE": {"n_reps": int, "group": str},
    "MEASURE_QC": {"gene_subset": list},
    "ADD_CONTROL": {"control_type": str},
    "FIT_MODEL": {"method": str},
    "COMMIT_HITS": {"gene_list": list},
}

ACTION_COSTS = {
    "ALLOCATE_REPLICATE": 1,
    "MEASURE_QC": 1,
    "ADD_CONTROL": 1,
    "FIT_MODEL": 2,
    "COMMIT_HITS": 0,
}


class ExperimentEngine:
    """Stateful sequential experiment engine for D1."""
    
    def __init__(self, master_seed: int, task_key: str, config: D1TaskConfig):
        self.master_seed = master_seed
        self.task_key = task_key
        self.config = config
        self.Y: Optional[np.ndarray] = None
        self.truth: Optional[HiddenTruth] = None
        self.step_count = 0
        self.total_cost = 0
        self.max_budget = 20
        self.done = False
        self.trajectory: list[dict] = []
        
    def reset(self) -> PublicObservation:
        """Reset engine and return initial observation."""
        self.Y, self.truth = generate_task(self.master_seed, self.task_key, self.config)
        self.step_count = 0
        self.total_cost = 0
        self.done = False
        self.trajectory = []
        return get_public_observation(self.Y, self.truth, step=0)
    
    def validate_action(self, action: Action) -> tuple[bool, str]:
        """Validate action. Returns (valid, error)."""
        if action.action_type not in VALID_ACTIONS:
            return False, f"Unknown action: {action.action_type}"
        
        if self.done:
            return False, "Episode already done"
        
        if self.total_cost + action.cost > self.max_budget:
            return False, f"Budget exceeded: {self.total_cost + action.cost} > {self.max_budget}"
        
        # Type validation
        expected = VALID_ACTIONS[action.action_type]
        for param, typ in expected.items():
            if param not in action.parameters:
                return False, f"Missing parameter: {param}"
            if not isinstance(action.parameters[param], typ):
                return False, f"Wrong type for {param}: expected {typ}"
        
        return True, ""
    
    def step(self, action: Action) -> StepResult:
        """Execute one action and return observation."""
        if self.done:
            return StepResult(
                observation=get_public_observation(self.Y, self.truth, self.step_count),
                reward=0, done=True, info={}, error="Already done"
            )
        
        # Validate
        valid, error = self.validate_action(action)
        if not valid:
            return StepResult(
                observation=get_public_observation(self.Y, self.truth, self.step_count),
                reward=0, done=False, info={"error": error}, error=error
            )
        
        # Execute
        self.step_count += 1
        self.total_cost += action.cost
        
        # Record trajectory
        self.trajectory.append({
            "step": self.step_count,
            "action": action.action_type,
            "parameters": {k: v for k, v in action.parameters.items() if k != "gene_list"},
            "cost": action.cost,
            "timestamp": time.time(),
        })
        
        # Check if done
        if action.action_type == "COMMIT_HITS":
            self.done = True
            return StepResult(
                observation=get_public_observation(self.Y, self.truth, self.step_count),
                reward=0, done=True, info={"submitted": True}
            )
        
        return StepResult(
            observation=get_public_observation(self.Y, self.truth, self.step_count),
            reward=0, done=False, info={}
        )
    
    def get_public_view(self) -> dict:
        """Get candidate-safe public view (no hidden truth)."""
        return {
            "step": self.step_count,
            "total_cost": self.total_cost,
            "max_budget": self.max_budget,
            "done": self.done,
            "trajectory": self.trajectory,
        }
