import numpy as np

from sbtq.dslit import fringe_visibility, screen_grid, toy_amplitudes
from sbtq.eraser import (
    conditional_path_states_pm,
    marked_joint_density,
    pattern_from_path_density,
)


def test_quantum_eraser_metrics() -> None:
    x = screen_grid(xmin=-10.0, xmax=10.0, n=4000)
    psi_a, psi_b = toy_amplitudes(x, sigma=5.0, k=6.0)

    rho_joint = marked_joint_density()
    states = conditional_path_states_pm(rho_joint)

    rho_path_plus = states["rho_path_plus"]
    rho_path_minus = states["rho_path_minus"]
    rho_path_uncond = states["rho_path_unconditional"]

    p_uncond = pattern_from_path_density(rho_path_uncond, psi_a, psi_b)
    p_plus = pattern_from_path_density(rho_path_plus, psi_a, psi_b)
    p_minus = pattern_from_path_density(rho_path_minus, psi_a, psi_b)

    p_mix = 0.5 * (np.abs(psi_a) ** 2 + np.abs(psi_b) ** 2)

    v_uncond = fringe_visibility(p_uncond, p_mix, mask_threshold=0.2)
    v_plus = fringe_visibility(p_plus, p_mix, mask_threshold=0.2)
    v_minus = fringe_visibility(p_minus, p_mix, mask_threshold=0.2)

    mask = p_mix >= 0.2 * float(np.max(p_mix))
    r_plus = (p_plus / p_mix)[mask]
    r_minus = (p_minus / p_mix)[mask]
    c_plus = r_plus - np.mean(r_plus)
    c_minus = r_minus - np.mean(r_minus)
    denom = np.linalg.norm(c_plus) * np.linalg.norm(c_minus)
    corr = float(np.dot(c_plus, c_minus) / denom) if denom > 0 else 0.0

    assert v_uncond <= 1e-3
    assert v_plus >= 0.95
    assert v_minus >= 0.95
    assert abs(v_plus - v_minus) <= 1e-3
    assert corr <= -0.95
