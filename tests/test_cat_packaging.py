import numpy as np

from sbtq.channels import dephase_subsystem
from sbtq.gates import basis_ket, cnot_matrix, pure_density
from sbtq.quantum import partial_trace, trace_distance


def _purity(rho: np.ndarray) -> float:
    return float(np.trace(rho @ rho).real)


def test_cat_packaging_metrics() -> None:
    ket_plus = (basis_ket(1, 0) + basis_ket(1, 1)) / np.sqrt(2.0)
    ket0 = basis_ket(1, 0)
    psi = np.kron(np.kron(ket_plus, ket0), ket0)
    rho_init = pure_density(psi)

    cnot_sa = cnot_matrix(3, control=0, target=1)
    cnot_ae = cnot_matrix(3, control=1, target=2)

    rho_after_measure = cnot_sa @ rho_init @ cnot_sa.conj().T
    rho_sae = cnot_ae @ rho_after_measure @ cnot_ae.conj().T

    rho_sa_before = partial_trace(rho_after_measure, dims=[2, 2, 2], keep=[0, 1])
    rho_sa_after = partial_trace(rho_sae, dims=[2, 2, 2], keep=[0, 1])

    rho_sa_pack = dephase_subsystem(rho_sa_before, dims=[2, 2], target=1)

    ket00 = np.kron(basis_ket(1, 0), basis_ket(1, 0))
    ket11 = np.kron(basis_ket(1, 1), basis_ket(1, 1))
    rho_mix = 0.5 * pure_density(ket00) + 0.5 * pure_density(ket11)

    purity_sa_before = _purity(rho_sa_before)
    purity_sae = _purity(rho_sae)
    purity_sa_after = _purity(rho_sa_after)

    dist_pack_vs_env = trace_distance(rho_sa_pack, rho_sa_after)
    dist_pack_vs_mix = trace_distance(rho_sa_pack, rho_mix)
    idempotence_error = trace_distance(
        dephase_subsystem(rho_sa_pack, dims=[2, 2], target=1), rho_sa_pack
    )

    assert purity_sa_before >= 1 - 1e-12
    assert purity_sae >= 1 - 1e-12
    assert purity_sa_after <= 0.5000000001
    assert dist_pack_vs_env <= 1e-12
    assert dist_pack_vs_mix <= 1e-12
    assert idempotence_error <= 1e-12
