"""Quantum eraser experiment with explicit environment qubit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from sbtq.dslit import fringe_visibility, screen_grid, toy_amplitudes
from sbtq.eraser import (
    conditional_path_states_pm,
    marked_joint_density,
    pattern_from_path_density,
)

EXPERIMENT_NAME = "quantum_eraser"
ARTIFACTS = [
    "figures/quantum_eraser_unconditional.png",
    "figures/quantum_eraser_conditional.png",
    "results/quantum_eraser.json",
]


def run(out_dir: Path, seed: int = 0) -> dict:
    xmin = -10.0
    xmax = 10.0
    n = 4000
    sigma = 5.0
    k = 6.0
    mask_threshold = 0.2

    _ = seed

    x = screen_grid(xmin=xmin, xmax=xmax, n=n)
    psi_a, psi_b = toy_amplitudes(x, sigma=sigma, k=k)

    rho_joint = marked_joint_density()
    states = conditional_path_states_pm(rho_joint)

    p_plus = float(states["p_plus"])
    p_minus = float(states["p_minus"])
    rho_path_plus = states["rho_path_plus"]
    rho_path_minus = states["rho_path_minus"]
    rho_path_uncond = states["rho_path_unconditional"]

    p_uncond = pattern_from_path_density(rho_path_uncond, psi_a, psi_b)
    p_plus_pat = pattern_from_path_density(rho_path_plus, psi_a, psi_b)
    p_minus_pat = pattern_from_path_density(rho_path_minus, psi_a, psi_b)

    p_mix = 0.5 * (np.abs(psi_a) ** 2 + np.abs(psi_b) ** 2)

    v_uncond = fringe_visibility(p_uncond, p_mix, mask_threshold=mask_threshold)
    v_plus = fringe_visibility(p_plus_pat, p_mix, mask_threshold=mask_threshold)
    v_minus = fringe_visibility(p_minus_pat, p_mix, mask_threshold=mask_threshold)

    mask = p_mix >= mask_threshold * float(np.max(p_mix))
    r_plus = (p_plus_pat / p_mix)[mask]
    r_minus = (p_minus_pat / p_mix)[mask]
    c_plus = r_plus - np.mean(r_plus)
    c_minus = r_minus - np.mean(r_minus)
    denom = np.linalg.norm(c_plus) * np.linalg.norm(c_minus)
    corr = float(np.dot(c_plus, c_minus) / denom) if denom > 0 else 0.0

    if v_uncond > 1e-3:
        raise AssertionError("Unconditional visibility exceeds 1e-3.")
    if v_plus < 0.95 or v_minus < 0.95:
        raise AssertionError("Conditional visibility below 0.95.")
    if abs(v_plus - v_minus) > 1e-3:
        raise AssertionError("Conditional visibilities differ by more than 1e-3.")
    if corr > -0.95:
        raise AssertionError("Fringe anticorrelation is weaker than -0.95.")

    figures_dir = out_dir / "figures"
    results_dir = out_dir / "results"
    figures_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 4.5))
    plt.plot(x, p_uncond, label="P_uncond")
    plt.plot(x, p_mix, "k--", alpha=0.6, label="P_mix")
    plt.xlabel("x")
    plt.ylabel("P(x)")
    plt.title("Quantum eraser: unconditional")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "quantum_eraser_unconditional.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.plot(x, p_plus_pat, label="P_plus")
    plt.plot(x, p_minus_pat, label="P_minus")
    plt.plot(x, p_uncond, "k--", alpha=0.5, label="P_uncond")
    plt.xlabel("x")
    plt.ylabel("P(x)")
    plt.title("Quantum eraser: conditional")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "quantum_eraser_conditional.png", dpi=150)
    plt.close()

    payload = {
        "model": "marked_path_env_qubit_pm_measure",
        "params": {
            "sigma": sigma,
            "k": k,
            "mask_threshold": mask_threshold,
            "xmin": xmin,
            "xmax": xmax,
            "n": n,
        },
        "p_plus": p_plus,
        "p_minus": p_minus,
        "visibility_unconditional": v_uncond,
        "visibility_plus": v_plus,
        "visibility_minus": v_minus,
        "visibility_diff": abs(v_plus - v_minus),
        "fringe_anticorrelation": corr,
    }

    json_path = results_dir / "quantum_eraser.json"
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
