import numpy as np

from sbtq.quantum import dephase, dephase_in_basis, trace_distance


def _rotation(theta: float) -> np.ndarray:
    c = float(np.cos(theta))
    s = float(np.sin(theta))
    return np.array([[c, s], [-s, c]], dtype=complex)


def test_dephase_contexts_mismatch() -> None:
    rho0 = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    h = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
    theta = float(np.pi / 6.0)
    u_theta = _rotation(theta)

    dz = dephase
    dx = lambda r: dephase_in_basis(r, h)
    dtheta = lambda r: dephase_in_basis(r, u_theta)

    mismatch_zx = trace_distance(dz(dx(rho0)), dx(dz(rho0)))
    mismatch_zt = trace_distance(dz(dtheta(rho0)), dtheta(dz(rho0)))

    assert mismatch_zt > 1e-3
    assert mismatch_zx < 1e-10

    rho = rho0
    maxmix = np.eye(2, dtype=complex) / 2.0
    distances = []
    for _ in range(4):
        distances.append(float(trace_distance(rho, maxmix)))
        rho = dz(dtheta(rho))

    assert distances[1] <= distances[0] + 1e-12
    assert distances[2] <= distances[1] + 1e-12
    assert distances[3] <= distances[2] + 1e-12
