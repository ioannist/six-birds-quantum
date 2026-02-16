"""Markov packaging utilities for two-basin chains."""

from __future__ import annotations

import numpy as np

from sbtq.closure import tv_distance


def make_two_basin_chain(
    n_per_basin: int = 10, leak: float = 0.02, lazy: float = 0.5
) -> np.ndarray:
    """Create a two-basin lazy ring chain with portal leak."""
    if n_per_basin <= 1:
        raise ValueError("n_per_basin must be > 1.")
    if not (0.0 <= leak <= 1.0):
        raise ValueError("leak must be in [0,1].")
    if not (0.0 <= lazy <= 1.0):
        raise ValueError("lazy must be in [0,1].")

    n = n_per_basin
    total = 2 * n
    p = np.zeros((total, total), dtype=float)

    step = (1.0 - lazy) / 2.0

    def ring_left(i: int) -> int:
        return (i - 1) % n

    def ring_right(i: int) -> int:
        return (i + 1) % n

    # Basin 0 indices 0..n-1
    for i in range(n):
        left = ring_left(i)
        right = ring_right(i)
        if i == 0:
            scale = 1.0 - leak
            p[i, i] = lazy * scale
            p[i, left] = step * scale
            p[i, right] = step * scale
            p[i, n] = leak
        else:
            p[i, i] = lazy
            p[i, left] = step
            p[i, right] = step

    # Basin 1 indices n..2n-1
    for i in range(n, 2 * n):
        j = i - n
        left = n + ring_left(j)
        right = n + ring_right(j)
        if i == n:
            scale = 1.0 - leak
            p[i, i] = lazy * scale
            p[i, left] = step * scale
            p[i, right] = step * scale
            p[i, 0] = leak
        else:
            p[i, i] = lazy
            p[i, left] = step
            p[i, right] = step

    if not np.allclose(p.sum(axis=1), 1.0):
        raise ValueError("Transition matrix rows do not sum to 1.")
    return p


def lens_two_basin(n_per_basin: int) -> np.ndarray:
    """Return basin label lens for two basins."""
    if n_per_basin <= 0:
        raise ValueError("n_per_basin must be positive.")
    n = n_per_basin
    f = np.zeros(2 * n, dtype=int)
    f[n:] = 1
    return f


def prototype_uniform(n_per_basin: int, basin: int) -> np.ndarray:
    """Uniform prototype over basin states."""
    if n_per_basin <= 0:
        raise ValueError("n_per_basin must be positive.")
    if basin not in (0, 1):
        raise ValueError("basin must be 0 or 1.")
    n = n_per_basin
    total = 2 * n
    mu = np.zeros(total, dtype=float)
    if basin == 0:
        mu[:n] = 1.0 / n
    else:
        mu[n:] = 1.0 / n
    return mu


def Q_f(mu: np.ndarray, f: np.ndarray) -> np.ndarray:
    """Coarse distribution over basin labels."""
    mu_arr = np.asarray(mu, dtype=float)
    f_arr = np.asarray(f)
    if mu_arr.ndim != 1 or f_arr.ndim != 1:
        raise ValueError("mu and f must be 1D.")
    if mu_arr.shape[0] != f_arr.shape[0]:
        raise ValueError("mu and f must have same length.")
    nu = np.zeros(2, dtype=float)
    nu[0] = float(mu_arr[f_arr == 0].sum())
    nu[1] = float(mu_arr[f_arr == 1].sum())
    return nu


def U_f(nu: np.ndarray, n_per_basin: int) -> np.ndarray:
    """Lift a basin distribution back to state space via uniform prototypes."""
    nu_arr = np.asarray(nu, dtype=float).reshape(-1)
    if nu_arr.shape[0] != 2:
        raise ValueError("nu must have length 2.")
    u0 = prototype_uniform(n_per_basin, 0)
    u1 = prototype_uniform(n_per_basin, 1)
    return nu_arr[0] * u0 + nu_arr[1] * u1


def E_tau(
    mu: np.ndarray,
    P: np.ndarray,
    f: np.ndarray,
    n_per_basin: int,
    tau: int,
) -> np.ndarray:
    """Timescale packaging endomap."""
    if tau < 0:
        raise ValueError("tau must be nonnegative.")
    mu_arr = np.asarray(mu, dtype=float)
    if mu_arr.ndim != 1:
        raise ValueError("mu must be 1D.")
    P_tau = np.linalg.matrix_power(P, tau)
    mu2 = mu_arr @ P_tau
    nu = Q_f(mu2, f)
    return U_f(nu, n_per_basin)


def idempotence_defect_tau(
    P: np.ndarray, f: np.ndarray, n_per_basin: int, tau: int
) -> float:
    """Compute max idempotence defect over Dirac states."""
    total = 2 * n_per_basin
    max_defect = 0.0
    for z in range(total):
        mu = np.zeros(total, dtype=float)
        mu[z] = 1.0
        e1 = E_tau(mu, P, f, n_per_basin, tau)
        e2 = E_tau(e1, P, f, n_per_basin, tau)
        defect = tv_distance(e2, e1)
        if defect > max_defect:
            max_defect = defect
    return max_defect


def prototype_stability_tau(
    P: np.ndarray, f: np.ndarray, n_per_basin: int, tau: int
) -> dict[str, float]:
    """Compute prototype stability for each basin."""
    u0 = prototype_uniform(n_per_basin, 0)
    u1 = prototype_uniform(n_per_basin, 1)
    e0 = E_tau(u0, P, f, n_per_basin, tau)
    e1 = E_tau(u1, P, f, n_per_basin, tau)
    s0 = tv_distance(e0, u0)
    s1 = tv_distance(e1, u1)
    return {"s0": s0, "s1": s1, "s_max": max(s0, s1)}
