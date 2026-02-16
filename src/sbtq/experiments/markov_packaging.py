"""Markov timescale packaging experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from sbtq.markov import (
    idempotence_defect_tau,
    lens_two_basin,
    make_two_basin_chain,
    prototype_stability_tau,
)

EXPERIMENT_NAME = "markov_packaging"
ARTIFACTS = [
    "figures/markov_idempotence_vs_tau.png",
    "results/markov_packaging.json",
]


def run(out_dir: Path, seed: int = 0) -> dict:
    n_per_basin = 10
    leak = 0.02
    lazy = 0.5
    stability_threshold = 0.02
    taus = [1, 2, 3, 4, 5, 7, 10, 15, 22, 33, 50, 75, 100, 150, 200, 300, 400, 500, 700, 1000]

    _ = seed

    P = make_two_basin_chain(n_per_basin=n_per_basin, leak=leak, lazy=lazy)
    f = lens_two_basin(n_per_basin)

    delta = []
    smax = []

    for tau in taus:
        delta.append(idempotence_defect_tau(P, f, n_per_basin, tau))
        smax.append(prototype_stability_tau(P, f, n_per_basin, tau)["s_max"])

    # Longest strictly decreasing run
    best_len = 1
    best_start = taus[0]
    best_end = taus[0]
    cur_len = 1
    cur_start = taus[0]
    for i in range(1, len(taus)):
        if delta[i] < delta[i - 1] - 1e-12:
            cur_len += 1
        else:
            if cur_len > best_len:
                best_len = cur_len
                best_start = cur_start
                best_end = taus[i - 1]
            cur_len = 1
            cur_start = taus[i]
    if cur_len > best_len:
        best_len = cur_len
        best_start = cur_start
        best_end = taus[-1]

    tau_first_stable = None
    for tau, s in zip(taus, smax):
        if s <= stability_threshold:
            tau_first_stable = tau
            break

    if tau_first_stable is None:
        raise AssertionError("No tau meets stability threshold.")
    if best_len < 3:
        raise AssertionError("Best decreasing run length < 3.")

    figures_dir = out_dir / "figures"
    results_dir = out_dir / "results"
    figures_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(7, 4.5))
    plt.plot(taus, delta, "o-", label="idempotence defect")
    plt.plot(taus, smax, "o-", label="prototype stability")
    plt.xscale("log")
    plt.xlabel("tau")
    plt.ylabel("value")
    plt.title("Markov packaging vs tau")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "markov_idempotence_vs_tau.png", dpi=150)
    plt.close()

    payload = {
        "model": "two_basin_portal_leak_packaging",
        "params": {
            "n_per_basin": n_per_basin,
            "leak": leak,
            "lazy": lazy,
            "stability_threshold": stability_threshold,
        },
        "taus": taus,
        "delta": [float(v) for v in delta],
        "prototype_stability_max": [float(v) for v in smax],
        "tau_first_stable": tau_first_stable,
        "best_decreasing_run": {
            "length": best_len,
            "tau_start": best_start,
            "tau_end": best_end,
        },
    }

    json_path = results_dir / "markov_packaging.json"
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
