"""Simple quantum channels."""

from __future__ import annotations

import numpy as np


def kron_all(mats: list[np.ndarray]) -> np.ndarray:
    """Kronecker product over a list of matrices (left-to-right)."""
    if not mats:
        raise ValueError("mats must be non-empty.")
    out = np.asarray(mats[0])
    for mat in mats[1:]:
        out = np.kron(out, np.asarray(mat))
    return out


def dephase_subsystem(rho: np.ndarray, dims: list[int], target: int) -> np.ndarray:
    """Dephase a target subsystem in the computational basis."""
    rho_arr = np.asarray(rho)
    if rho_arr.ndim != 2 or rho_arr.shape[0] != rho_arr.shape[1]:
        raise ValueError("rho must be square.")
    if not dims:
        raise ValueError("dims must be non-empty.")
    if any(d <= 0 for d in dims):
        raise ValueError("dims entries must be positive.")
    if target < 0 or target >= len(dims):
        raise ValueError("target out of range.")

    dim_total = int(np.prod(dims))
    if rho_arr.shape[0] != dim_total:
        raise ValueError("rho dimension does not match dims product.")

    d_t = dims[target]
    proj_mats = []
    for k in range(d_t):
        ket = np.zeros(d_t, dtype=complex)
        ket[k] = 1.0
        proj = np.outer(ket, np.conjugate(ket))
        factors = [np.eye(d, dtype=complex) for d in dims]
        factors[target] = proj
        proj_mats.append(kron_all(factors))

    out = np.zeros_like(rho_arr, dtype=complex)
    for proj in proj_mats:
        out = out + proj @ rho_arr @ proj
    return out
