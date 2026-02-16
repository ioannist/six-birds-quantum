import numpy as np

from sbtq.dslit import (
    fringe_visibility,
    probability_with_overlap,
    screen_grid,
    toy_amplitudes,
)


def _visibility_for_gamma(gamma: float) -> float:
    x = screen_grid()
    psi_a, psi_b = toy_amplitudes(x)
    p, p_mix = probability_with_overlap(psi_a, psi_b, gamma=gamma)
    return fringe_visibility(p, p_mix)


def test_visibility_bounds() -> None:
    v0 = _visibility_for_gamma(0.0)
    v1 = _visibility_for_gamma(1.0)
    assert v0 <= 1e-3
    assert v1 >= 0.95
