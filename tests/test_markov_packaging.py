import numpy as np

from sbtq.markov import (
    idempotence_defect_tau,
    lens_two_basin,
    make_two_basin_chain,
    prototype_stability_tau,
)


def test_markov_packaging_small() -> None:
    n_per_basin = 4
    leak = 0.05
    lazy = 0.5
    taus = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]

    P = make_two_basin_chain(n_per_basin=n_per_basin, leak=leak, lazy=lazy)
    f = lens_two_basin(n_per_basin)

    stability = prototype_stability_tau(P, f, n_per_basin, tau=1)["s_max"]
    assert stability < 0.05

    delta_34 = idempotence_defect_tau(P, f, n_per_basin, tau=34)
    delta_610 = idempotence_defect_tau(P, f, n_per_basin, tau=610)
    assert delta_34 > delta_610

    for tau in taus:
        delta = idempotence_defect_tau(P, f, n_per_basin, tau)
        assert np.isfinite(delta)
        assert delta >= 0.0
