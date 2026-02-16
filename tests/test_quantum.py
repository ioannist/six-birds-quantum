import numpy as np

from sbtq.quantum import (
    apply_unitary,
    dagger,
    dephase,
    is_psd,
    partial_trace,
    random_density,
    trace_distance,
    unitary_from_hermitian,
)


def test_dephase_idempotent() -> None:
    rho = random_density(4, seed=123)
    once = dephase(rho)
    twice = dephase(once)
    assert np.allclose(twice, once, atol=1e-10)


def test_trace_distance_unitary_invariant() -> None:
    rho = random_density(3, seed=1)
    sigma = random_density(3, seed=2)
    rng = np.random.default_rng(3)
    X = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
    H = (X + dagger(X)) / 2.0
    U = unitary_from_hermitian(H, t=0.37)

    d1 = trace_distance(rho, sigma)
    d2 = trace_distance(apply_unitary(rho, U), apply_unitary(sigma, U))
    assert np.isclose(d1, d2, atol=1e-10)


def test_partial_trace_product_state() -> None:
    rho_a = random_density(2, seed=4)
    rho_b = random_density(3, seed=5)
    rho_ab = np.kron(rho_a, rho_b)

    reduced = partial_trace(rho_ab, dims=[2, 3], keep=[0])
    assert np.allclose(reduced, rho_a, atol=1e-10)
    assert np.isclose(np.trace(reduced), 1.0, atol=1e-10)
    assert is_psd(reduced, tol=1e-10)


def test_partial_trace_bell_state() -> None:
    phi = np.array([1.0, 0.0, 0.0, 1.0]) / np.sqrt(2.0)
    rho = np.outer(phi, np.conjugate(phi))

    reduced = partial_trace(rho, dims=[2, 2], keep=[0])
    target = np.eye(2) / 2.0
    assert np.allclose(reduced, target, atol=1e-10)
    assert np.isclose(np.trace(reduced), 1.0, atol=1e-10)
    assert is_psd(reduced, tol=1e-10)


def test_random_density_deterministic() -> None:
    rho1 = random_density(5, seed=7)
    rho2 = random_density(5, seed=7)
    assert np.allclose(rho1, rho2, atol=1e-12)
