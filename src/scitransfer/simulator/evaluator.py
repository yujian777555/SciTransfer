"""D1 Trusted Evaluator: FDP/Power/Cost scoring.

Runs in a separate context from the candidate. Receives hidden truth
and candidate artifact. Never exposes hidden truth to candidate.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np


@dataclass
class ScoreResult:
    """Raw scoring result - never fabricated."""
    fdp: float  # False Discovery Proportion
    power: float  # Realized power (or NaN if all-null)
    n_reported: int
    n_true_positives: int
    n_false_positives: int
    n_true_non_null: int
    sample_cost: int
    all_null: bool
    null_power: bool  # True if power is undefined (all-null)
    
    def to_dict(self) -> dict:
        return {
            "fdp": self.fdp,
            "power": self.power if not self.null_power else None,
            "n_reported": self.n_reported,
            "n_true_positives": self.n_true_positives,
            "n_false_positives": self.n_false_positives,
            "n_true_non_null": self.n_true_non_null,
            "sample_cost": self.sample_cost,
            "all_null": self.all_null,
            "null_power": self.null_power,
        }


def score_submission(
    reported_genes: list[int],
    true_non_null: list[int],
    sample_cost: int,
) -> ScoreResult:
    """Score candidate submission against hidden truth.
    
    This is the TRUSTED evaluator. Candidate must never see true_non_null.
    """
    R = len(reported_genes)  # total reported
    S = len(set(reported_genes) & set(true_non_null))  # true positives
    V = R - S  # false positives
    n_true = len(true_non_null)
    
    # FDP
    fdp = V / max(R, 1)
    
    # Power (undefined if all-null)
    all_null = n_true == 0
    if all_null:
        power = float("nan")
        null_power = True
    else:
        power = S / n_true
        null_power = False
    
    return ScoreResult(
        fdp=fdp,
        power=power,
        n_reported=R,
        n_true_positives=S,
        n_false_positives=V,
        n_true_non_null=n_true,
        sample_cost=sample_cost,
        all_null=all_null,
        null_power=null_power,
    )


def compute_utility(score: ScoreResult, w1: float = 0.4, w2: float = 0.4, w3: float = 0.2) -> float:
    """Compute scalar utility with fixed weights.
    
    Weights are frozen before evaluation. Report raw metrics alongside.
    """
    if score.null_power:
        # All-null: penalize false positives only
        return w1 * (1.0 - score.fdp) - w3 * score.sample_cost / 100.0
    return w1 * (1.0 - score.fdp) + w2 * score.power - w3 * score.sample_cost / 100.0
