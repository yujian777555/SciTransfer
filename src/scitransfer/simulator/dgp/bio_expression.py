"""D1 Corrected DGP: Fixed M1 dispersion, real batch assignment, proper identifiability."""
from __future__ import annotations

import hashlib
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class D1TaskConfig:
    """Configuration for D1 task generation (corrected)."""
    n_genes: int = 1000
    n_samples: int = 30
    n_batches: int = 2
    pi0: float = 0.8
    mu_alpha: float = 5.0
    sigma_alpha: float = 1.0
    phi0: float = 4.0  # M1 constant dispersion
    phi_shape: float = 2.0  # M2
    phi_rate: float = 0.5  # M2
    sigma_gamma: float = 0.0
    mu_beta: float = 0.0
    sigma_beta: float = 1.0
    sigma_size: float = 0.5
    mechanism: str = "M1"


@dataclass
class HiddenTruth:
    """Hidden state - NEVER accessible to candidate."""
    true_non_null: set[int]
    beta: np.ndarray
    phi: np.ndarray
    gamma: np.ndarray
    alpha: np.ndarray
    size_factors: np.ndarray
    treatment: np.ndarray
    batch: np.ndarray
    master_seed: int
    task_key: str
    Y_full: np.ndarray  # Full count matrix


def _derive_seed(master_seed: int, task_key: str, component: str) -> int:
    h = hashlib.sha256(f"{master_seed}:{task_key}:{component}".encode()).hexdigest()
    return int(h[:8], 16)


def generate_task(master_seed: int, task_key: str, config: D1TaskConfig) -> HiddenTruth:
    """Generate D1 task with corrected DGP."""
    G, N = config.n_genes, config.n_samples
    
    rng_data = np.random.default_rng(_derive_seed(master_seed, task_key, "data"))
    rng_assign = np.random.default_rng(_derive_seed(master_seed, task_key, "assign"))
    
    # Batch assignment: equal sizes
    batch = np.zeros(N, dtype=int)
    for b in range(config.n_batches):
        start = b * (N // config.n_batches)
        end = (b + 1) * (N // config.n_batches) if b < config.n_batches - 1 else N
        batch[start:end] = b
    
    # Treatment: randomized within batch (ensures overlap)
    treatment = np.zeros(N, dtype=int)
    for b in range(config.n_batches):
        idx = np.where(batch == b)[0]
        n_treat = max(1, len(idx) // 2)  # At least 1 treated per batch
        perm = rng_assign.permutation(len(idx))
        treatment[idx[perm[:n_treat]]] = 1
    
    # Identifiability: rank + within-batch overlap
    design = np.column_stack([np.ones(N), treatment] + [
        (batch == b).astype(float) for b in range(1, config.n_batches)
    ])
    rank = np.linalg.matrix_rank(design)
    expected_rank = 2 + (config.n_batches - 1)
    if rank < expected_rank:
        raise ValueError(f"Unidentifiable: rank={rank} < {expected_rank}")
    
    # Within-batch overlap check
    for b in range(config.n_batches):
        idx = np.where(batch == b)[0]
        if treatment[idx].sum() == 0 or treatment[idx].sum() == len(idx):
            raise ValueError(f"No overlap in batch {b}")
    
    # Hidden parameters
    alpha = rng_data.normal(config.mu_alpha, config.sigma_alpha, G)
    
    # CORRECTED: M1 constant phi, M2 variable phi
    if config.mechanism == "M1":
        phi = np.full(G, config.phi0)
    else:  # M2
        phi = rng_data.gamma(config.phi_shape, 1.0 / config.phi_rate, G)
    
    # Sparse treatment effects
    is_null = rng_data.random(G) < config.pi0
    beta = np.zeros(G)
    non_null = ~is_null
    beta[non_null] = rng_data.normal(config.mu_beta, config.sigma_beta, non_null.sum())
    
    # Batch effects
    gamma = rng_data.normal(0, config.sigma_gamma, (G, config.n_batches))
    
    # Size factors
    size_factors = rng_data.lognormal(0, config.sigma_size, N)
    
    # Generate counts
    log_mu = (
        np.log(size_factors)[np.newaxis, :]
        + alpha[:, np.newaxis]
        + beta[:, np.newaxis] * treatment[np.newaxis, :]
        + gamma[:, batch]
    )
    mu = np.exp(log_mu)
    
    # NB via gamma-poisson
    lambda_gj = rng_data.gamma(phi[:, np.newaxis], mu / phi[:, np.newaxis])
    Y = rng_data.poisson(lambda_gj)
    
    return HiddenTruth(
        true_non_null=set(np.where(non_null)[0].tolist()),
        beta=beta, phi=phi, gamma=gamma, alpha=alpha,
        size_factors=size_factors, treatment=treatment, batch=batch,
        master_seed=master_seed, task_key=task_key, Y_full=Y,
    )
