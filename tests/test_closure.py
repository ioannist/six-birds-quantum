import numpy as np

from sbtq.closure import (
    fixed_points_by_sampling,
    fixed_points_finite,
    idempotence_defect,
    is_idempotent_map,
    route_mismatch,
    trace_distance_metric,
)
from sbtq.quantum import apply_unitary, dephase, random_density


def test_dephase_idempotent_via_interface() -> None:
    def sampler(i: int) -> np.ndarray:
        return random_density(d=3, seed=100 + i)

    samples = [sampler(i) for i in range(3)]
    assert is_idempotent_map(dephase, samples, tol=1e-10, metric=trace_distance_metric)

    defect = idempotence_defect(dephase, sampler, trace_distance_metric, n=3)
    assert defect <= 1e-10


def test_route_mismatch_nonzero_hadamard() -> None:
    H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
    rho0 = np.array([[1, 0], [0, 0]], dtype=complex)

    def g(rho: np.ndarray) -> np.ndarray:
        return apply_unitary(rho, H)

    def sampler(_: int) -> np.ndarray:
        return rho0

    mismatch = route_mismatch(dephase, g, sampler, trace_distance_metric, n=1)
    assert mismatch > 1e-6


def test_fixed_points_finite() -> None:
    def E(x: int) -> int:
        return 0

    universe = [0, 1, 2]
    assert fixed_points_finite(E, universe) == [0]


def test_fixed_points_by_sampling_dephase() -> None:
    rho_diag = np.diag([0.7, 0.3])

    def sampler(_: int) -> np.ndarray:
        return rho_diag

    fixed = fixed_points_by_sampling(dephase, sampler, trace_distance_metric, tol=1e-12, n=1)
    assert len(fixed) == 1
    assert np.allclose(fixed[0], rho_diag, atol=1e-12)
