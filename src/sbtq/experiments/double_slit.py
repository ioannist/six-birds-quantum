"""Double-slit toy experiment with environment overlap."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from sbtq.dslit import (
    fringe_visibility,
    probability_with_overlap,
    screen_grid,
    toy_amplitudes,
)

EXPERIMENT_NAME = "double_slit"
ARTIFACTS = [
    "figures/double_slit_patterns.png",
    "figures/double_slit_visibility.png",
    "results/double_slit.json",
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

    gamma_list = [1.0, 0.7, 0.3, 0.0]
    visibilities: list[float] = []
    patterns: list[np.ndarray] = []
    p_mix_ref: np.ndarray | None = None

    for gamma in gamma_list:
        p, p_mix = probability_with_overlap(psi_a, psi_b, gamma=gamma)
        if p_mix_ref is None:
            p_mix_ref = p_mix
        v = fringe_visibility(p, p_mix, mask_threshold=mask_threshold)
        visibilities.append(float(v))
        patterns.append(p)

    tol = 1e-6
    for i in range(1, len(visibilities)):
        if visibilities[i] > visibilities[i - 1] + tol:
            raise AssertionError("Visibility is not monotone nonincreasing in |gamma|.")

    if visibilities[-1] > 1e-3:
        raise AssertionError("Visibility at gamma=0 exceeds 1e-3.")

    figures_dir = out_dir / "figures"
    results_dir = out_dir / "results"
    figures_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 4.5))
    for gamma, p in zip(gamma_list, patterns):
        plt.plot(x, p, label=f"|gamma|={gamma}")
    if p_mix_ref is not None:
        plt.plot(x, p_mix_ref, "k--", alpha=0.6, label="P_mix")
    plt.xlabel("x")
    plt.ylabel("P(x)")
    plt.title("Double-slit patterns with overlap")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "double_slit_patterns.png", dpi=150)
    plt.close()

    plt.figure(figsize=(6, 4))
    plt.plot(gamma_list, visibilities, "o-")
    plt.xlabel("|gamma|")
    plt.ylabel("Visibility")
    plt.title("Fringe visibility vs overlap")
    plt.ylim(0.0, 1.05)
    plt.tight_layout()
    plt.savefig(figures_dir / "double_slit_visibility.png", dpi=150)
    plt.close()

    payload = {
        "model": "toy_gaussian_phase_ramp",
        "params": {
            "sigma": sigma,
            "k": k,
            "mask_threshold": mask_threshold,
            "xmin": xmin,
            "xmax": xmax,
            "n": n,
        },
        "gamma_abs": gamma_list,
        "visibility": visibilities,
        "monotone_nonincreasing": True,
        "visibility_at_zero_gamma": visibilities[-1],
    }

    json_path = results_dir / "double_slit.json"
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
