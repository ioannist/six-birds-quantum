"""Route mismatch experiment: dephase vs unitary."""

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
    partial_dephase,
    random_density,
    trace_distance,
    unitary_from_hermitian,
)

EXPERIMENT_NAME = "route_mismatch"
ARTIFACTS = [
    "figures/route_mismatch_vs_time.png",
    "figures/route_mismatch_heatmap.png",
    "results/route_mismatch.json",
]


def run(out_dir: Path, seed: int = 0) -> dict:
    d = 3
    base_seed = 123 + seed
    t_min = 0.0
    t_max = 5.0
    n_t = 200
    t_grid = np.linspace(t_min, t_max, n_t)
    p_grid = np.linspace(0.0, 1.0, 21)

    rng = np.random.default_rng(base_seed)
    x = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    h_rand = (x + x.conj().T) / 2.0

    diag_vals = rng.normal(size=d)
    h_diag = np.diag(diag_vals)

    rho = random_density(d=d, seed=base_seed + 1)

    m_rand = np.zeros_like(t_grid, dtype=float)
    m_diag = np.zeros_like(t_grid, dtype=float)

    for i, t in enumerate(t_grid):
        u = unitary_from_hermitian(h_rand, t)
        route1 = dephase(apply_unitary(rho, u))
        route2 = apply_unitary(dephase(rho), u)
        m_rand[i] = trace_distance(route1, route2)

        u_diag = unitary_from_hermitian(h_diag, t)
        route1_d = dephase(apply_unitary(rho, u_diag))
        route2_d = apply_unitary(dephase(rho), u_diag)
        m_diag[i] = trace_distance(route1_d, route2_d)

    heat = np.zeros((len(p_grid), len(t_grid)), dtype=float)

    for pi, p in enumerate(p_grid):
        for ti, t in enumerate(t_grid):
            u = unitary_from_hermitian(h_rand, t)
            route1 = partial_dephase(apply_unitary(rho, u), p)
            route2 = apply_unitary(partial_dephase(rho, p), u)
            heat[pi, ti] = trace_distance(route1, route2)

    max_rand = float(np.max(m_rand))
    max_diag = float(np.max(m_diag))
    max_heat_p0 = float(np.max(heat[0, :]))

    if max_rand <= 1e-3:
        raise AssertionError("max_mismatch_random_H must exceed 1e-3.")
    if max_diag >= 1e-10:
        raise AssertionError("max_mismatch_diagonal_H must be < 1e-10.")
    if max_heat_p0 >= 1e-10:
        raise AssertionError("max_heat_p0 must be < 1e-10.")

    figures_dir = out_dir / "figures"
    results_dir = out_dir / "results"
    figures_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 4.5))
    plt.plot(t_grid, m_rand, label="random H")
    plt.plot(t_grid, m_diag, label="diagonal H")
    plt.xlabel("t")
    plt.ylabel("mismatch")
    plt.title("Route mismatch vs time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "route_mismatch_vs_time.png", dpi=150)
    plt.close()

    plt.figure(figsize=(7, 4.8))
    plt.imshow(
        heat,
        aspect="auto",
        origin="lower",
        extent=[t_min, t_max, p_grid[0], p_grid[-1]],
    )
    plt.colorbar(label="mismatch")
    plt.xlabel("t")
    plt.ylabel("p")
    plt.title("Route mismatch heatmap")
    plt.tight_layout()
    plt.savefig(figures_dir / "route_mismatch_heatmap.png", dpi=150)
    plt.close()

    payload = {
        "model": "route_mismatch_dephase_vs_unitary",
        "params": {
            "d": d,
            "seed": base_seed,
            "t_min": t_min,
            "t_max": t_max,
            "n_t": n_t,
            "p_grid_n": len(p_grid),
        },
        "max_mismatch_random_H": max_rand,
        "max_mismatch_diagonal_H": max_diag,
        "max_heat_p0": max_heat_p0,
        "t_grid": [float(v) for v in t_grid],
        "mismatch_random_H": [float(v) for v in m_rand],
        "mismatch_diagonal_H": [float(v) for v in m_diag],
        "p_grid": [float(v) for v in p_grid],
        "heatmap_random_H": [[float(v) for v in row] for row in heat],
    }

    json_path = results_dir / "route_mismatch.json"
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
