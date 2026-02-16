"""Quantum eraser helpers with explicit environment qubit."""

from __future__ import annotations

import numpy as np

from sbtq.quantum import partial_trace


def ket0() -> np.ndarray:
    """Return |0> ket."""
    return np.array([1.0, 0.0], dtype=complex)


def ket1() -> np.ndarray:
    """Return |1> ket."""
    return np.array([0.0, 1.0], dtype=complex)


def ket_plus() -> np.ndarray:
    """Return |+> = (|0> + |1>)/sqrt(2)."""
    return (ket0() + ket1()) / np.sqrt(2.0)


def ket_minus() -> np.ndarray:
    """Return |-> = (|0> - |1>)/sqrt(2)."""
    return (ket0() - ket1()) / np.sqrt(2.0)


def projector(ket: np.ndarray) -> np.ndarray:
    """Return |ket><ket| projector."""
    ket_arr = np.asarray(ket).reshape(-1)
    return np.outer(ket_arr, np.conjugate(ket_arr))


def marked_joint_density() -> np.ndarray:
    """Return |Psi><Psi| with |Psi> = (|A,0> + |B,1>)/sqrt(2)."""
    psi = np.array([1.0, 0.0, 0.0, 1.0], dtype=complex) / np.sqrt(2.0)
    return projector(psi)


def conditional_path_states_pm(rho_joint: np.ndarray) -> dict[str, np.ndarray | float]:
    """Return conditional path states after env measurement in +/- basis."""
    rho = np.asarray(rho_joint)
    if rho.shape != (4, 4):
        raise ValueError("rho_joint must be 4x4.")

    p_plus_ket = ket_plus()
    p_minus_ket = ket_minus()
    p_plus = projector(p_plus_ket)
    p_minus = projector(p_minus_ket)

    i_path = np.eye(2, dtype=complex)
    proj_plus = np.kron(i_path, p_plus)
    proj_minus = np.kron(i_path, p_minus)

    rho_plus = proj_plus @ rho @ proj_plus
    rho_minus = proj_minus @ rho @ proj_minus

    p_plus_val = float(np.trace(rho_plus).real)
    p_minus_val = float(np.trace(rho_minus).real)

    if np.isclose(p_plus_val, 0.0, atol=1e-12, rtol=0.0):
        raise ValueError("p_plus is zero; cannot condition.")
    if np.isclose(p_minus_val, 0.0, atol=1e-12, rtol=0.0):
        raise ValueError("p_minus is zero; cannot condition.")

    rho_path_plus = partial_trace(rho_plus, dims=[2, 2], keep=[0]) / p_plus_val
    rho_path_minus = partial_trace(rho_minus, dims=[2, 2], keep=[0]) / p_minus_val
    rho_path_uncond = partial_trace(rho, dims=[2, 2], keep=[0])

    return {
        "p_plus": p_plus_val,
        "rho_path_plus": rho_path_plus,
        "p_minus": p_minus_val,
        "rho_path_minus": rho_path_minus,
        "rho_path_unconditional": rho_path_uncond,
    }


def pattern_from_path_density(
    rho_path: np.ndarray, psi_a: np.ndarray, psi_b: np.ndarray
) -> np.ndarray:
    """Compute screen pattern P(x) = psi^dag rho_path psi."""
    rho = np.asarray(rho_path)
    psi = np.vstack([np.asarray(psi_a), np.asarray(psi_b)])
    p = np.einsum("ix,ij,jx->x", np.conjugate(psi), rho, psi).real
    return np.maximum(p, 0.0)
