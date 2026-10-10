"""D1 Bioinformatics DGP: Batch-aware differential expression.

Generates synthetic count data with negative binomial distribution,
treatment effects, batch confounders, and hidden truth.
"""
from __future__ import annotations

import hashlib
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class D1TaskConfig:
    """Configuration for D1 task generation."""
    n_genes: int = 1000
    n_samples: int = 30
    n_batches: int = 2
    pi0: float = 0.8  # fraction of null genes
    sigma_alpha: float = 1.0
    mu_alpha: float = 5.0
    phi_shape: float = 2.0
    phi_rate: float = 0.5
    sigma_gamma: float = 0.0  # batch effect strength
    mu_beta: float = 0.0
    sigma_beta: float = 1.0
    sigma_size: float = 0.5
    mechanism: str = "M1"  # M1=unconfounded, M2=partially confounded


@dataclass
class HiddenTruth:
    """Hidden state - NEVER accessible to candidate."""
    true_non_null: list[int]  # gene indices with beta != 0
    beta: np.ndarray  # treatment effects
    phi: np.ndarray  # dispersion
    gamma: np.ndarray  # batch effects
    alpha: np.ndarray  # baseline
    size_factors: np.ndarray
    treatment: np.ndarray  # t_j
    batch: np.ndarray  # b_j
    master_seed: int
    task_key: str


@dataclass
class PublicObservation:
    """Candidate-facing observation."""
    gene_means_control: np.ndarray
    gene_means_treatment: np.ndarray
    gene_vars_control: np.ndarray
    gene_vars_treatment: np.ndarray
    sample_counts_per_group: dict
    qc_metrics: dict
    step: int


def _derive_seed(master_seed: int, task_key: str, component: str) -> int:
    """Cryptographic derivation of stable component seed."""
    h = hashlib.sha256(f"{master_seed}:{task_key}:{component}".encode()).hexdigest()
    return int(h[:8], 16)


def generate_task(master_seed: int, task_key: str, config: D1TaskConfig) -> tuple[np.ndarray, HiddenTruth]:
    """Generate D1 task data. Returns (expression_matrix, hidden_truth)."""
    G, N = config.n_genes, config.n_samples
    
    # Independent RNG streams
    rng_data = np.random.default_rng(_derive_seed(master_seed, task_key, "data"))
    rng_assignment = np.random.default_rng(_derive_seed(master_seed, task_key, "assign"))
    
    # Treatment and batch assignment
    if config.mechanism == "M1":
        # Random treatment within batches
        batch = np.repeat(np.arange(config.n_batches), N // config.n_batches)
        if len(batch) < N:
            batch = np.concatenate([batch, np.full(N - len(batch), 0)])
        treatment = np.zeros(N, dtype=int)
        for b in range(config.n_batches):
            idx = np.where(batch == b)[0]
            n_treat = len(idx) // 2
            treatment[idx[:n_treat]] = 1
    else:  # M2: partially confounded
        batch = np.repeat(np.arange(config.n_batches), N // config.n_batches)
        if len(batch) < N:
            batch = np.concatenate([batch, np.full(N - len(batch), 0)])
        # Treatment partially correlated with batch
        treatment = np.zeros(N, dtype=int)
        for b in range(config.n_batches):
            idx = np.where(batch == b)[0]
            # Higher batch -> more treated (confounding)
            n_treat = int(len(idx) * (0.3 + 0.4 * b))
            treatment[idx[:n_treat]] = 1
    
    # Identifiability check
    design = np.column_stack([np.ones(N), treatment] + [
        (batch == b).astype(float) for b in range(1, config.n_batches)
    ])
    rank = np.linalg.matrix_rank(design)
    expected_rank = 1 + 1 + (config.n_batches - 1)
    if rank < expected_rank:
        raise ValueError(f"Unidentifiable design: rank={rank} < expected={expected_rank}")
    
    # Hidden parameters
    alpha = rng_data.normal(config.mu_alpha, config.sigma_alpha, G)
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
    
    # Negative binomial via gamma-poisson mixture
    lambda_gj = rng_data.gamma(phi[:, np.newaxis], mu / phi[:, np.newaxis])
    Y = rng_data.poisson(lambda_gj)
    
    truth = HiddenTruth(
        true_non_null=np.where(non_null)[0].tolist(),
        beta=beta, phi=phi, gamma=gamma, alpha=alpha,
        size_factors=size_factors, treatment=treatment, batch=batch,
        master_seed=master_seed, task_key=task_key,
    )
    
    return Y, truth


def get_public_observation(Y: np.ndarray, truth: HiddenTruth, step: int = 0) -> PublicObservation:
    """Extract candidate-safe public observation from data."""
    treatment = truth.treatment
    G, N = Y.shape
    
    ctrl_idx = np.where(treatment == 0)[0]
    treat_idx = np.where(treatment == 1)[0]
    
    return PublicObservation(
        gene_means_control=Y[:, ctrl_idx].mean(axis=1) if len(ctrl_idx) > 0 else np.zeros(G),
        gene_means_treatment=Y[:, treat_idx].mean(axis=1) if len(treat_idx) > 0 else np.zeros(G),
        gene_vars_control=Y[:, ctrl_idx].var(axis=1) if len(ctrl_idx) > 0 else np.zeros(G),
        gene_vars_treatment=Y[:, treat_idx].var(axis=1) if len(treat_idx) > 0 else np.zeros(G),
        sample_counts_per_group={"control": len(ctrl_idx), "treatment": len(treat_idx)},
        qc_metrics={"total_counts": float(Y.sum()), "mean_depth": float(Y.sum(axis=0).mean())},
        step=step,
    )
