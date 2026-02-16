"""Dephasing in incompatible bases: contextual mismatch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from sbtq.quantum import (
    apply_unitary,
    dephase,
    dephase_in_basis,
    trace_distance,
)

EXPERIMENT_NAME = "dephase_contexts"
ARTIFACTS = [
    "figures/dephase_contexts_mismatch.png",
    "results/dephase_contexts.json",
]


def _hadamard() -> np.ndarray:
    return (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)


def _rotation(theta: float) -> np.ndarray:
    c = float(np.cos(theta))
    s = float(np.sin(theta))
    return np.array([[c, s], [-s, c]], dtype=complex)


def _mismatch_for_theta(rho: np.ndarray, theta: float) -> float:
    u = _rotation(theta)
    dz = dephase
    dtheta = lambda r: dephase_in_basis(r, u)
    route1 = dz(dtheta(rho))
    route2 = dtheta(dz(rho))
    return float(trace_distance(route1, route2))


def run(out_dir: Path, seed: int = 0) -> dict:
    _ = seed

    rho0 = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)

    h = _hadamard()
    dz = dephase
    dx = lambda r: dephase_in_basis(r, h)

    theta = float(np.pi / 6.0)
    u_theta = _rotation(theta)
    dtheta = lambda r: dephase_in_basis(r, u_theta)

    mismatch_zx = trace_distance(dz(dx(rho0)), dx(dz(rho0)))
    mismatch_zt = trace_distance(dz(dtheta(rho0)), dtheta(dz(rho0)))

    k_steps = 8
    rho = rho0
    distances = []
    maxmix = np.eye(2, dtype=complex) / 2.0
    for _ in range(k_steps):
        distances.append(float(trace_distance(rho, maxmix)))
        rho = dz(dtheta(rho))

    distance_monotone = True
    for i in range(len(distances) - 1):
        if distances[i + 1] > distances[i] + 1e-12:
            distance_monotone = False
            break

    if float(mismatch_zt) <= 1e-3:
        raise AssertionError("mismatch_Z_tilt must exceed 1e-3.")
    if float(mismatch_zx) >= 1e-10:
        raise AssertionError("mismatch_ZX must be < 1e-10.")
    if not distance_monotone:
        raise AssertionError("distance_to_maxmix is not monotone nonincreasing.")
    if distances[-1] >= 1e-2:
        raise AssertionError("final distance to maximally mixed is too large.")

    figures_dir = out_dir / "figures"
    results_dir = out_dir / "results"
    figures_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    theta_grid = np.linspace(0.0, np.pi / 2.0, 200)
    mismatch_grid = [_mismatch_for_theta(rho0, t) for t in theta_grid]

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))

    axes[0].plot(theta_grid, mismatch_grid, label="mismatch(θ)")
    for tmark, label in [
        (0.0, "0"),
        (np.pi / 4.0, "π/4"),
        (np.pi / 2.0, "π/2"),
        (theta, "π/6"),
    ]:
        axes[0].axvline(tmark, color="k", linestyle="--", alpha=0.5)
        axes[0].text(tmark, max(mismatch_grid) * 0.9, label, rotation=90, va="top")
    axes[0].set_xlabel("θ (radians)")
    axes[0].set_ylabel("mismatch")
    axes[0].set_title("Mismatch vs basis tilt")

    axes[1].plot(range(len(distances)), distances, "o-")
    axes[1].set_xlabel("iteration k")
    axes[1].set_ylabel("distance to I/2")
    axes[1].set_title("Convergence to maximally mixed")

    plt.tight_layout()
    plt.savefig(figures_dir / "dephase_contexts_mismatch.png", dpi=150)
    plt.close(fig)

    payload = {
        "model": "dephase_in_incompatible_bases",
        "theta_rad": theta,
        "mismatch_ZX": float(mismatch_zx),
        "mismatch_Z_tilt": float(mismatch_zt),
        "distance_to_maxmix": distances,
        "distance_to_maxmix_monotone": bool(distance_monotone),
    }

    json_path = results_dir / "dephase_contexts.json"
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
