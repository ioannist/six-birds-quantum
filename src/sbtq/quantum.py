"""Quantum linear algebra utilities."""

from __future__ import annotations

from typing import Iterable

import numpy as np
from scipy.linalg import expm


def dagger(A: np.ndarray) -> np.ndarray:
    """Return the conjugate transpose of A."""
    return np.conjugate(np.asarray(A)).T


def commutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Return the commutator [A, B] = A @ B - B @ A."""
    A_arr = np.asarray(A)
    B_arr = np.asarray(B)
    return A_arr @ B_arr - B_arr @ A_arr


def is_hermitian(A: np.ndarray, tol: float = 1e-10) -> bool:
    """Check whether A is Hermitian within tolerance."""
    A_arr = np.asarray(A)
    if A_arr.ndim != 2 or A_arr.shape[0] != A_arr.shape[1]:
        return False
    return np.allclose(A_arr, dagger(A_arr), atol=tol, rtol=0.0)


def is_psd(A: np.ndarray, tol: float = 1e-10) -> bool:
    """Check whether A is positive semidefinite within tolerance."""
    A_arr = np.asarray(A)
    if A_arr.ndim != 2 or A_arr.shape[0] != A_arr.shape[1]:
        return False
    herm = (A_arr + dagger(A_arr)) / 2.0
    eigvals = np.linalg.eigvalsh(herm)
    return bool(np.all(eigvals >= -tol))


def is_density_matrix(rho: np.ndarray, tol: float = 1e-10) -> bool:
    """Check whether rho is a valid density matrix within tolerance."""
    rho_arr = np.asarray(rho)
    if rho_arr.ndim != 2 or rho_arr.shape[0] != rho_arr.shape[1]:
        return False
    if not is_hermitian(rho_arr, tol=tol):
        return False
    if not is_psd(rho_arr, tol=tol):
        return False
    tr = np.trace(rho_arr)
    return bool(np.isclose(tr, 1.0, atol=tol, rtol=0.0))


def normalize_density(rho: np.ndarray) -> np.ndarray:
    """Symmetrize and normalize a density matrix to trace 1."""
    rho_arr = np.asarray(rho)
    herm = (rho_arr + dagger(rho_arr)) / 2.0
    tr = np.trace(herm)
    if np.isclose(tr, 0.0, atol=1e-12, rtol=0.0):
        raise ValueError("Cannot normalize density matrix with near-zero trace.")
    return herm / tr


def random_density(d: int, rank: int | None = None, seed: int | None = None) -> np.ndarray:
    """Generate a random density matrix of dimension d with optional rank."""
    if d <= 0:
        raise ValueError("Dimension d must be positive.")
    r = d if rank is None else int(rank)
    if r <= 0 or r > d:
        raise ValueError("rank must satisfy 1 <= rank <= d.")
    rng = np.random.default_rng(seed)
    real = rng.normal(size=(d, r))
    imag = rng.normal(size=(d, r))
    G = real + 1j * imag
    rho = G @ dagger(G)
    return normalize_density(rho)


def unitary_from_hermitian(H: np.ndarray, t: float) -> np.ndarray:
    """Compute U = expm(-1j * H * t) for Hermitian H."""
    H_arr = np.asarray(H)
    if not is_hermitian(H_arr):
        raise ValueError("H must be Hermitian.")
    return expm(-1j * H_arr * t)


def apply_unitary(rho: np.ndarray, U: np.ndarray) -> np.ndarray:
    """Apply a unitary evolution to a density matrix."""
    rho_arr = np.asarray(rho)
    U_arr = np.asarray(U)
    return U_arr @ rho_arr @ dagger(U_arr)


def trace_distance(rho: np.ndarray, sigma: np.ndarray, tol: float = 1e-12) -> float:
    """Compute the trace distance between two density matrices."""
    delta = np.asarray(rho) - np.asarray(sigma)
    herm = (delta + dagger(delta)) / 2.0
    eigvals = np.linalg.eigvalsh(herm)
    return 0.5 * float(np.sum(np.abs(eigvals)))


def partial_trace(
    rho: np.ndarray,
    dims: Iterable[int],
    keep: Iterable[int],
) -> np.ndarray:
    """Trace out subsystems not listed in keep."""
    rho_arr = np.asarray(rho)
    if rho_arr.ndim != 2 or rho_arr.shape[0] != rho_arr.shape[1]:
        raise ValueError("rho must be a square matrix.")
    dims_list = [int(d) for d in dims]
    keep_list = [int(k) for k in keep]
    n = len(dims_list)
    if n == 0:
        raise ValueError("dims must be non-empty.")
    if any(d <= 0 for d in dims_list):
        raise ValueError("All dims must be positive.")
    if len(set(keep_list)) != len(keep_list):
        raise ValueError("keep indices must be unique.")
    if any(k < 0 or k >= n for k in keep_list):
        raise ValueError("keep indices out of range.")
    total_dim = int(np.prod(dims_list))
    if rho_arr.shape[0] != total_dim:
        raise ValueError("rho dimension does not match product of dims.")

    traceout = [i for i in range(n) if i not in keep_list]
    dims_keep = [dims_list[i] for i in keep_list]
    dims_trace = [dims_list[i] for i in traceout]
    d_keep = int(np.prod(dims_keep)) if dims_keep else 1
    d_tr = int(np.prod(dims_trace)) if dims_trace else 1

    reshaped = rho_arr.reshape(*dims_list, *dims_list)
    perm = keep_list + traceout + [i + n for i in keep_list] + [i + n for i in traceout]
    permuted = np.transpose(reshaped, axes=perm)
    permuted = permuted.reshape(d_keep, d_tr, d_keep, d_tr)
    return np.trace(permuted, axis1=1, axis2=3)


def dephase(rho: np.ndarray, basis: str = "computational") -> np.ndarray:
    """Dephase a density matrix in the given basis."""
    if basis != "computational":
        raise NotImplementedError("Only the computational basis is supported.")
    rho_arr = np.asarray(rho)
    return np.diag(np.diag(rho_arr))


def partial_dephase(rho: np.ndarray, p: float) -> np.ndarray:
    """Mix rho with its dephased version with probability p."""
    if p < 0.0 or p > 1.0:
        raise ValueError("p must satisfy 0 <= p <= 1.")
    rho_arr = np.asarray(rho)
    return (1.0 - p) * rho_arr + p * dephase(rho_arr)


def dephase_in_basis(rho: np.ndarray, U: np.ndarray) -> np.ndarray:
    """Dephase rho in the basis defined by unitary U."""
    rho_rot = apply_unitary(rho, U)
    rho_rot_d = dephase(rho_rot)
    return apply_unitary(rho_rot_d, dagger(U))
