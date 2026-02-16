import numpy as np

from sbtq.quantum import (
    apply_unitary,
    dephase,
    partial_dephase,
    random_density,
    trace_distance,
    unitary_from_hermitian,
)


def test_route_mismatch_small() -> None:
    d = 2
    seed = 7
    t_grid = [0.0, 0.7, 1.3]
    p_grid = [0.0, 1.0]

    rng = np.random.default_rng(seed)
    x = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    h_rand = (x + x.conj().T) / 2.0

    diag_vals = rng.normal(size=d)
    h_diag = np.diag(diag_vals)

    rho = random_density(d=d, seed=seed + 1)

    m_rand = []
    m_diag = []
    for t in t_grid:
        u = unitary_from_hermitian(h_rand, t)
        route1 = dephase(apply_unitary(rho, u))
        route2 = apply_unitary(dephase(rho), u)
        m_rand.append(trace_distance(route1, route2))

        u_diag = unitary_from_hermitian(h_diag, t)
        route1_d = dephase(apply_unitary(rho, u_diag))
        route2_d = apply_unitary(dephase(rho), u_diag)
        m_diag.append(trace_distance(route1_d, route2_d))

    assert any(m > 1e-6 for t, m in zip(t_grid, m_rand) if t > 0.0)
    assert all(m < 1e-10 for m in m_diag)

    for p in p_grid:
        for t in t_grid:
            u = unitary_from_hermitian(h_rand, t)
            route1 = partial_dephase(apply_unitary(rho, u), p)
            route2 = apply_unitary(partial_dephase(rho, p), u)
            mismatch = trace_distance(route1, route2)
            if p == 0.0:
                assert mismatch < 1e-10
