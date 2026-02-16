"""Closure utilities and mismatch metrics."""

from __future__ import annotations

from collections.abc import Iterable, Callable
from typing import Any

import numpy as np

from sbtq.quantum import trace_distance


ArrayLike = np.ndarray


def tv_distance(p: np.ndarray, q: np.ndarray) -> float:
    """Return 1/2 L1 distance between probability vectors p and q."""
    p_arr = np.asarray(p)
    q_arr = np.asarray(q)
    if p_arr.ndim != 1 or q_arr.ndim != 1:
        raise ValueError("p and q must be 1D vectors.")
    if p_arr.shape != q_arr.shape:
        raise ValueError("p and q must have the same shape.")
    return 0.5 * float(np.sum(np.abs(p_arr - q_arr)))


def trace_distance_metric(rho: np.ndarray, sigma: np.ndarray) -> float:
    """Wrapper around sbtq.quantum.trace_distance."""
    return trace_distance(rho, sigma)


def frobenius_distance(A: np.ndarray, B: np.ndarray) -> float:
    """Frobenius norm distance between matrices."""
    return float(np.linalg.norm(np.asarray(A) - np.asarray(B)))


def is_idempotent_map(
    f: Callable[[Any], Any],
    samples: Iterable[Any],
    tol: float,
    metric: Callable[[Any, Any], float] | None = None,
) -> bool:
    """Check if f(f(x)) == f(x) within tolerance over samples."""
    metric_fn = metric or frobenius_distance
    max_defect = 0.0
    for x in samples:
        defect = metric_fn(f(f(x)), f(x))
        if defect > max_defect:
            max_defect = defect
    return max_defect <= tol


def idempotence_defect(
    f: Callable[[Any], Any],
    sampler: Callable[[int], Any],
    metric: Callable[[Any, Any], float],
    n: int = 100,
) -> float:
    """Return maximum idempotence defect over n deterministic samples."""
    if n <= 0:
        raise ValueError("n must be positive.")
    max_defect = 0.0
    for i in range(n):
        x = sampler(i)
        defect = metric(f(f(x)), f(x))
        if defect > max_defect:
            max_defect = defect
    return max_defect


def route_mismatch(
    f: Callable[[Any], Any],
    g: Callable[[Any], Any],
    sampler: Callable[[int], Any],
    metric: Callable[[Any, Any], float],
    n: int = 100,
) -> float:
    """Return max distance between f(g(x)) and g(f(x)) over n samples."""
    if n <= 0:
        raise ValueError("n must be positive.")
    max_mismatch = 0.0
    for i in range(n):
        x = sampler(i)
        mismatch = metric(f(g(x)), g(f(x)))
        if mismatch > max_mismatch:
            max_mismatch = mismatch
    return max_mismatch


def fixed_points_finite(
    E: Callable[[Any], Any],
    universe: Iterable[Any],
    eq: Callable[[Any, Any], bool] | None = None,
) -> list[Any]:
    """Return all fixed points of E inside a finite universe."""
    eq_fn = eq or (lambda a, b: a == b)
    return [x for x in universe if eq_fn(E(x), x)]


def fixed_points_by_sampling(
    E: Callable[[Any], Any],
    sampler: Callable[[int], Any],
    metric: Callable[[Any, Any], float],
    tol: float,
    n: int = 100,
) -> list[Any]:
    """Return sampled points with residual metric(E(x), x) <= tol.

    The sampler should be deterministic when built with deterministic seed logic.
    """
    if n <= 0:
        raise ValueError("n must be positive.")
    fixed: list[Any] = []
    for i in range(n):
        x = sampler(i)
        if metric(E(x), x) <= tol:
            fixed.append(x)
    return fixed
