"""Simple gate helpers for small qubit systems."""

from __future__ import annotations

import numpy as np


def basis_ket(n: int, index: int) -> np.ndarray:
    """Return computational basis ket |index> of length 2**n."""
    if n <= 0:
        raise ValueError("n must be positive.")
    dim = 2**n
    if index < 0 or index >= dim:
        raise ValueError("index out of range.")
    ket = np.zeros(dim, dtype=complex)
    ket[index] = 1.0
    return ket


def pure_density(ket: np.ndarray) -> np.ndarray:
    """Return |ket><ket| density matrix."""
    ket_arr = np.asarray(ket).reshape(-1)
    return np.outer(ket_arr, np.conjugate(ket_arr))


def cnot_matrix(n: int, control: int, target: int) -> np.ndarray:
    """Return the CNOT unitary on n qubits with MSB-first indexing."""
    if n <= 0:
        raise ValueError("n must be positive.")
    if control == target:
        raise ValueError("control and target must differ.")
    if not (0 <= control < n) or not (0 <= target < n):
        raise ValueError("control/target out of range.")

    dim = 2**n
    mat = np.zeros((dim, dim), dtype=complex)
    for basis_index in range(dim):
        bits = list(format(basis_index, f"0{n}b"))
        if bits[control] == "1":
            bits[target] = "0" if bits[target] == "1" else "1"
        out_index = int("".join(bits), 2)
        mat[out_index, basis_index] = 1.0
    return mat
