"""Cat packaging experiment: environment record vs dephase channel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from sbtq.channels import dephase_subsystem
from sbtq.gates import basis_ket, cnot_matrix, pure_density
from sbtq.quantum import partial_trace, trace_distance

EXPERIMENT_NAME = "cat_packaging"
ARTIFACTS = ["figures/cat_packaging.png", "results/cat_packaging.json"]


def purity(rho: np.ndarray) -> float:
    return float(np.trace(rho @ rho).real)


def run(out_dir: Path, seed: int = 0) -> dict:
    _ = seed

    # Initial state |+>_S |0>_A |0>_E
    ket_plus = (basis_ket(1, 0) + basis_ket(1, 1)) / np.sqrt(2.0)
    ket0 = basis_ket(1, 0)
    psi = np.kron(np.kron(ket_plus, ket0), ket0)
    rho_init = pure_density(psi)

    # Apply CNOT S->A then A->E
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

    purity_sa_before = purity(rho_sa_before)
    purity_sae = purity(rho_sae)
    purity_sa_after = purity(rho_sa_after)

    dist_pack_vs_env = trace_distance(rho_sa_pack, rho_sa_after)
    dist_pack_vs_mix = trace_distance(rho_sa_pack, rho_mix)
    idempotence_error = trace_distance(
        dephase_subsystem(rho_sa_pack, dims=[2, 2], target=1), rho_sa_pack
    )

    if purity_sa_before < 1 - 1e-12:
        raise AssertionError("purity_SA_before_record below threshold.")
    if purity_sae < 1 - 1e-12:
        raise AssertionError("purity_SAE_after_record below threshold.")
    if purity_sa_after > 0.5000000001:
        raise AssertionError("purity_SA_after_record above 0.5.")
    if dist_pack_vs_env > 1e-12:
        raise AssertionError("dist_pack_vs_env exceeds tolerance.")
    if dist_pack_vs_mix > 1e-12:
        raise AssertionError("dist_pack_vs_mix exceeds tolerance.")
    if idempotence_error > 1e-12:
        raise AssertionError("idempotence_error exceeds tolerance.")

    figures_dir = out_dir / "figures"
    results_dir = out_dir / "results"
    figures_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    axes[0].imshow(rho_sa_before.real, vmin=-0.5, vmax=0.5, cmap="coolwarm")
    axes[0].set_title("Re(rho_SA_before)")
    axes[1].imshow(rho_sa_after.real, vmin=-0.5, vmax=0.5, cmap="coolwarm")
    axes[1].set_title("Re(rho_SA_after)")
    diff = (rho_sa_after - rho_mix).real
    im2 = axes[2].imshow(diff, vmin=-0.5, vmax=0.5, cmap="coolwarm")
    axes[2].set_title("Re(rho_after - rho_mix)")
    fig.colorbar(im2, ax=axes, shrink=0.8)
    plt.tight_layout()
    plt.savefig(figures_dir / "cat_packaging.png", dpi=150)
    plt.close(fig)

    payload = {
        "model": "cat_SAE_cnot_measure_and_record",
        "purity_SA_before_record": purity_sa_before,
        "purity_SAE_after_record": purity_sae,
        "purity_SA_after_record": purity_sa_after,
        "dist_pack_vs_env": dist_pack_vs_env,
        "dist_pack_vs_mix": dist_pack_vs_mix,
        "idempotence_error": idempotence_error,
    }

    json_path = results_dir / "cat_packaging.json"
    json_path.write_text(json.dumps(payload, sort_keys=True, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    run(args.out, seed=args.seed)


if __name__ == "__main__":
    main()
