import numpy as np

from sbtq.eraser import ket0, ket1, ket_plus, ket_minus, projector
from sbtq.quantum import partial_trace, trace_distance


def _bell_state() -> np.ndarray:
    ket00 = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    ket11 = np.array([0.0, 0.0, 0.0, 1.0], dtype=complex)
    psi = (ket00 + ket11) / np.sqrt(2.0)
    return np.outer(psi, np.conjugate(psi))


def _measure_alice(rho_ab: np.ndarray, projectors: list[np.ndarray]) -> tuple[list[float], list[np.ndarray], np.ndarray]:
    i2 = np.eye(2, dtype=complex)
    probs: list[float] = []
    rho_b_cond: list[np.ndarray] = []
    rho_ab_uncond = np.zeros_like(rho_ab)
    for p in projectors:
        m = np.kron(p, i2)
        rho_a = m @ rho_ab @ m
        p_a = float(np.trace(rho_a).real)
        probs.append(p_a)
        rho_ab_uncond = rho_ab_uncond + rho_a
        rho_b = partial_trace(rho_a, dims=[2, 2], keep=[1]) / p_a
        rho_b_cond.append(rho_b)
    rho_b_uncond = partial_trace(rho_ab_uncond, dims=[2, 2], keep=[1])
    return probs, rho_b_cond, rho_b_uncond


def test_no_signalling_epr() -> None:
    rho_ab = _bell_state()
    rho_b_before = partial_trace(rho_ab, dims=[2, 2], keep=[1])

    p0z = projector(ket0())
    p1z = projector(ket1())
    probs_z, rho_b_cond_z, rho_b_uncond_z = _measure_alice(rho_ab, [p0z, p1z])

    p_plus = projector(ket_plus())
    p_minus = projector(ket_minus())
    probs_x, rho_b_cond_x, rho_b_uncond_x = _measure_alice(rho_ab, [p_plus, p_minus])

    no_sig_z = trace_distance(rho_b_before, rho_b_uncond_z)
    no_sig_x = trace_distance(rho_b_before, rho_b_uncond_x)
    cond_z = trace_distance(rho_b_cond_z[0], rho_b_cond_z[1])
    cond_x = trace_distance(rho_b_cond_x[0], rho_b_cond_x[1])

    assert no_sig_z <= 1e-12
    assert no_sig_x <= 1e-12
    assert cond_z >= 0.9
    assert cond_x >= 0.9

    for p in probs_z + probs_x:
        assert abs(p - 0.5) <= 1e-12
