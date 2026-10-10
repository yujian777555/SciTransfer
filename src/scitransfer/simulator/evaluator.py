"""D1 Corrected Evaluator: pure function, neutral utility, no strategy ID."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ScoreResult:
    """Raw scoring result."""
    fdp: float
    power: Optional[float]  # None if all-null
    n_reported: int
    n_true_positives: int
    n_false_positives: int
    n_true_non_null: int
    sample_cost: int
    all_null: bool
    utility: float  # Regret-based, neutral

    def to_dict(self) -> dict:
        return {
            "fdp": self.fdp,
            "power": self.power,
            "n_reported": self.n_reported,
            "n_true_positives": self.n_true_positives,
            "n_false_positives": self.n_false_positives,
            "n_true_non_null": self.n_true_non_null,
            "sample_cost": self.sample_cost,
            "all_null": self.all_null,
            "utility": self.utility,
        }


def score_submission(
    reported_genes: list[int],
    true_non_null: set[int],
    sample_cost: int,
) -> ScoreResult:
    """Score candidate submission. PURE FUNCTION - no strategy ID.

    Uses set semantics: duplicates do not inflate FDP.
    """
    reported = set(reported_genes)  # Deduplicate
    R = len(reported)
    S = len(reported & true_non_null)
    V = R - S
    n_true = len(true_non_null)

    # FDP
    fdp = V / max(R, 1)

    # Power (None if all-null)
    all_null = n_true == 0
    power = None if all_null else S / n_true

    # CORRECTED: Regret-based neutral utility
    # Empty submission: power=0, fdp=0 → utility = 0
    # Perfect: power=1, fdp=0 → utility = 1/cost
    # Bad: power=0, fdp=1 → utility = -1/cost
    if all_null:
        utility = 0.0  # Undefined power, no discovery
    else:
        cost_factor = max(sample_cost, 1)
        utility = (power - fdp) / cost_factor

    return ScoreResult(
        fdp=fdp,
        power=power,
        n_reported=R,
        n_true_positives=S,
        n_false_positives=V,
        n_true_non_null=n_true,
        sample_cost=sample_cost,
        all_null=all_null,
        utility=utility,
    )
