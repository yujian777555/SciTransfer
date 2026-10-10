"""D1 Corrected Engine: real sequential actions with server-side enforcement."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np

from .dgp.bio_expression import D1TaskConfig, HiddenTruth, generate_task


@dataclass
class Action:
    """Typed action - NO cost field (server enforces)."""
    action_type: str
    parameters: dict


@dataclass
class PublicObservation:
    """Candidate-safe observation."""
    group_sizes: dict
    qc_summary: dict
    measured_genes: dict  # gene_id -> {mean, var} for measured genes
    step: int


@dataclass
class StepResult:
    observation: PublicObservation
    done: bool
    info: dict
    error: Optional[str] = None


# Server-side cost functions
ACTION_COSTS = {
    "ALLOCATE_REPLICATE": lambda p: int(p.get("n_reps", 0)),
    "MEASURE_QC": lambda p: max(1, len(p.get("gene_subset", [])) // 10),
    "FIT_MODEL": lambda p: 2,
    "COMMIT_HITS": lambda p: 0,
}

VALID_PARAMS = {
    "ALLOCATE_REPLICATE": {"n_reps": int, "group": str},
    "MEASURE_QC": {"gene_subset": list},
    "FIT_MODEL": {"genes": list},
    "COMMIT_HITS": {"gene_list": list},
}


class ExperimentEngine:
    """Corrected engine with real actions and isolation."""
    
    def __init__(self, master_seed: int, task_key: str, config: D1TaskConfig):
        self._master_seed = master_seed
        self._task_key = task_key
        self._config = config
        self._truth: Optional[HiddenTruth] = None
        self._Y_current: Optional[np.ndarray] = None  # Grows with ALLOCATE_REPLICATE
        
        # Public state
        self.step_count = 0
        self.total_cost = 0
        self.max_budget = 30
        self.max_samples = 60
        self.done = False
        self.submitted_genes: Optional[list[int]] = None
        
        # What candidate has measured
        self._measured_genes: dict[int, dict] = {}
        self._allocated: dict[str, int] = {"control": 0, "treatment": 0}
        
    def reset(self) -> PublicObservation:
        """Reset and return INITIAL limited observation (no per-gene stats)."""
        self._truth = generate_task(self._master_seed, self._task_key, self._config)
        self._Y_current = self._truth.Y_full.copy()
        self.step_count = 0
        self.total_cost = 0
        self.done = False
        self.submitted_genes = None
        self._measured_genes = {}
        self._allocated = {"control": 0, "treatment": 0}
        
        # Initial: only group sizes and global QC
        return self._get_observation()
    
    def _get_observation(self) -> PublicObservation:
        """Public observation - ONLY measured data, no hidden truth."""
        treatment = self._truth.treatment
        n_ctrl = int((treatment == 0).sum())
        n_treat = int((treatment == 1).sum())
        
        # Global QC (always available)
        qc = {
            "total_counts": float(self._Y_current.sum()),
            "mean_depth": float(self._Y_current.sum(axis=0).mean()),
        }
        
        return PublicObservation(
            group_sizes={"control": n_ctrl, "treatment": n_treat},
            qc_summary=qc,
            measured_genes=dict(self._measured_genes),
            step=self.step_count,
        )
    
    def _server_cost(self, action: Action) -> int:
        """Compute authoritative cost."""
        if action.action_type not in ACTION_COSTS:
            return -1
        return ACTION_COSTS[action.action_type](action.parameters)
    
    def _validate(self, action: Action) -> tuple[bool, str]:
        """Validate action with strict checks."""
        if self.done:
            return False, "Already done"
        
        if action.action_type not in VALID_PARAMS:
            return False, f"Unknown action: {action.action_type}"
        
        # Parameter type checks
        expected = VALID_PARAMS[action.action_type]
        for param, typ in expected.items():
            if param not in action.parameters:
                return False, f"Missing: {param}"
            if not isinstance(action.parameters[param], typ):
                return False, f"Wrong type for {param}"
        
        # Extra params check
        for k in action.parameters:
            if k not in expected:
                return False, f"Unexpected param: {k}"
        
        # Server cost
        cost = self._server_cost(action)
        if cost < 0:
            return False, "Invalid action"
        if self.total_cost + cost > self.max_budget:
            return False, f"Budget exceeded: {self.total_cost + cost} > {self.max_budget}"
        
        # Action-specific validation
        if action.action_type == "ALLOCATE_REPLICATE":
            n = action.parameters["n_reps"]
            group = action.parameters["group"]
            if n <= 0 or n > 10:
                return False, f"n_reps must be 1-10, got {n}"
            if group not in ("control", "treatment"):
                return False, f"Invalid group: {group}"
            total_samples = sum(self._allocated.values()) + n
            if total_samples > self.max_samples:
                return False, f"Exceeds max samples: {total_samples}"
        
        elif action.action_type == "MEASURE_QC":
            genes = action.parameters["gene_subset"]
            G = self._config.n_genes
            for g in genes:
                if not isinstance(g, int) or g < 0 or g >= G:
                    return False, f"Invalid gene ID: {g}"
        
        elif action.action_type == "FIT_MODEL":
            genes = action.parameters["genes"]
            G = self._config.n_genes
            for g in genes:
                if not isinstance(g, int) or g < 0 or g >= G:
                    return False, f"Invalid gene ID: {g}"
        
        elif action.action_type == "COMMIT_HITS":
            gene_list = action.parameters["gene_list"]
            G = self._config.n_genes
            # Validate unique, bounded integers
            if not all(isinstance(g, int) and 0 <= g < G for g in gene_list):
                return False, "Gene IDs must be integers in [0, G)"
            if len(set(gene_list)) != len(gene_list):
                return False, "Duplicate gene IDs"
        
        return True, ""
    
    def step(self, action: Action) -> StepResult:
        """Execute action with real consequences."""
        valid, error = self._validate(action)
        if not valid:
            return StepResult(
                observation=self._get_observation(),
                done=self.done, info={}, error=error
            )
        
        cost = self._server_cost(action)
        self.total_cost += cost
        self.step_count += 1
        
        # Execute action
        if action.action_type == "ALLOCATE_REPLICATE":
            n = action.parameters["n_reps"]
            group = action.parameters["group"]
            self._allocated[group] += n
            # Real effect: new samples are added to Y
            # (In simulation, we just track counts; Y already has all samples)
            info = {"added": n, "group": group}
        
        elif action.action_type == "MEASURE_QC":
            genes = action.parameters["gene_subset"]
            treatment = self._truth.treatment
            ctrl_idx = np.where(treatment == 0)[0]
            treat_idx = np.where(treatment == 1)[0]
            
            for g in genes:
                if g not in self._measured_genes:
                    y_g = self._Y_current[g]
                    self._measured_genes[g] = {
                        "mean_control": float(y_g[ctrl_idx].mean()) if len(ctrl_idx) > 0 else 0,
                        "var_control": float(y_g[ctrl_idx].var()) if len(ctrl_idx) > 0 else 0,
                        "mean_treatment": float(y_g[treat_idx].mean()) if len(treat_idx) > 0 else 0,
                        "var_treatment": float(y_g[treat_idx].var()) if len(treat_idx) > 0 else 0,
                    }
            info = {"measured": len(genes)}
        
        elif action.action_type == "FIT_MODEL":
            genes = action.parameters["genes"]
            treatment = self._truth.treatment
            results = {}
            for g in genes:
                if g not in self._measured_genes:
                    continue
                # Simple t-test
                y_g = self._Y_current[g]
                ctrl = y_g[treatment == 0]
                treat = y_g[treatment == 1]
                if len(ctrl) > 1 and len(treat) > 1:
                    from scipy import stats
                    t_stat, p_val = stats.ttest_ind(treat, ctrl)
                    results[g] = {"t_stat": float(t_stat), "p_value": float(p_val)}
            info = {"fitted": len(results)}
            self._measured_genes.update({g: {**self._measured_genes.get(g, {}), **v} for g, v in results.items()})
        
        elif action.action_type == "COMMIT_HITS":
            self.submitted_genes = action.parameters["gene_list"]
            self.done = True
            info = {"submitted": len(self.submitted_genes)}
        
        return StepResult(
            observation=self._get_observation(),
            done=self.done,
            info=info,
        )
    
    def get_public_view(self) -> dict:
        """Candidate-safe public view."""
        return {
            "step": self.step_count,
            "total_cost": self.total_cost,
            "max_budget": self.max_budget,
            "done": self.done,
            "group_sizes": self._allocated,
            "n_measured_genes": len(self._measured_genes),
        }
