"""Deterministic toy double-slit model with environment overlap."""

from __future__ import annotations

import numpy as np


def screen_grid(xmin: float = -10.0, xmax: float = 10.0, n: int = 4000) -> np.ndarray:
    """Return a 1D screen grid."""
    if n <= 1:
        raise ValueError("n must be > 1.")
    return np.linspace(xmin, xmax, n)


def toy_amplitudes(
    x: np.ndarray, sigma: float = 5.0, k: float = 6.0
) -> tuple[np.ndarray, np.ndarray]:
    """Return toy slit amplitudes with Gaussian envelope and phase ramp."""
    x_arr = np.asarray(x)
    g = np.exp(-(x_arr**2) / (2.0 * sigma**2))
    phi = k * x_arr
    psi_a = g * np.exp(0.5j * phi)
    psi_b = g * np.exp(-0.5j * phi)
    return psi_a, psi_b


def probability_with_overlap(
    psi_a: np.ndarray, psi_b: np.ndarray, gamma: complex
) -> tuple[np.ndarray, np.ndarray]:
    """Return total probability and mixture for a given overlap gamma."""
    psi_a_arr = np.asarray(psi_a)
    psi_b_arr = np.asarray(psi_b)
    p_mix = 0.5 * (np.abs(psi_a_arr) ** 2 + np.abs(psi_b_arr) ** 2)
    interference = np.real(np.conjugate(gamma) * np.conjugate(psi_a_arr) * psi_b_arr)
    p = p_mix + interference
    p = np.maximum(p, 0.0)
    return p, p_mix


def fringe_visibility(
    p: np.ndarray, p_mix: np.ndarray, mask_threshold: float = 0.2
) -> float:
    """Compute visibility on normalized pattern over a central mask."""
    p_arr = np.asarray(p)
    p_mix_arr = np.asarray(p_mix)
    if p_arr.shape != p_mix_arr.shape:
        raise ValueError("p and p_mix must have the same shape.")
    if p_mix_arr.size == 0:
        raise ValueError("p_mix is empty.")
    threshold = mask_threshold * float(np.max(p_mix_arr))
    mask = p_mix_arr >= threshold
    if not np.any(mask):
        return 0.0
    r = p_arr[mask] / p_mix_arr[mask]
    r_max = float(np.max(r))
    r_min = float(np.min(r))
    denom = r_max + r_min
    if np.isclose(denom, 0.0, atol=1e-12, rtol=0.0):
        return 0.0
    return (r_max - r_min) / denom
