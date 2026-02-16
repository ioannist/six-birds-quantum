"""No-signalling vs conditioning for an EPR pair."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from sbtq.eraser import ket0, ket1, ket_plus, ket_minus, projector
from sbtq.quantum import partial_trace, trace_distance

EXPERIMENT_NAME = "no_signalling_epr"
ARTIFACTS = [
    "figures/no_signalling_epr.png",
    "results/no_signalling_epr.json",
]


def _bell_state() -> np.ndarray:
    ket00 = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    ket11 = np.array([0.0, 0.0, 0.0, 1.0], dtype=complex)
    psi = (ket00 + ket11) / np.sqrt(2.0)
    return np.outer(psi, np.conjugate(psi))


def _measure_alice(
    rho_ab: np.ndarray, projectors: list[np.ndarray]
) -> tuple[list[float], list[np.ndarray], np.ndarray]:
    i2 = np.eye(2, dtype=complex)
    probs: list[float] = []
    rho_b_cond: list[np.ndarray] = []
    rho_ab_uncond = np.zeros_like(rho_ab)
    for p in projectors:
        m = np.kron(p, i2)
        rho_a = m @ rho_ab @ m
        p_a = float(np.trace(rho_a).real)
        probs.append(p_a)
        rho_ab_uncond = rho_ab_uncond + rho_a
        rho_b = partial_trace(rho_a, dims=[2, 2], keep=[1]) / p_a
        rho_b_cond.append(rho_b)
    rho_b_uncond = partial_trace(rho_ab_uncond, dims=[2, 2], keep=[1])
    return probs, rho_b_cond, rho_b_uncond


def run(out_dir: Path, seed: int = 0) -> dict:
    _ = seed

    rho_ab = _bell_state()
    rho_b_before = partial_trace(rho_ab, dims=[2, 2], keep=[1])

    # Z basis
    p0z = projector(ket0())
    p1z = projector(ket1())
    probs_z, rho_b_cond_z, rho_b_uncond_z = _measure_alice(rho_ab, [p0z, p1z])

    # X basis
    p_plus = projector(ket_plus())
    p_minus = projector(ket_minus())
    probs_x, rho_b_cond_x, rho_b_uncond_x = _measure_alice(rho_ab, [p_plus, p_minus])

    no_sig_z = trace_distance(rho_b_before, rho_b_uncond_z)
    no_sig_x = trace_distance(rho_b_before, rho_b_uncond_x)

    cond_dist_z = trace_distance(rho_b_cond_z[0], rho_b_cond_z[1])
    cond_dist_x = trace_distance(rho_b_cond_x[0], rho_b_cond_x[1])

    p0_z, p1_z = probs_z
    p_plus_x, p_minus_x = probs_x

    if no_sig_z > 1e-12:
        raise AssertionError("no_signalling_dist_Z exceeds 1e-12")
    if no_sig_x > 1e-12:
        raise AssertionError("no_signalling_dist_X exceeds 1e-12")
    if cond_dist_z < 0.9:
        raise AssertionError("cond_outcome_dist_Z below 0.9")
    if cond_dist_x < 0.9:
        raise AssertionError("cond_outcome_dist_X below 0.9")
    for p in [p0_z, p1_z, p_plus_x, p_minus_x]:
        if abs(p - 0.5) > 1e-12:
            raise AssertionError("outcome probability not ~0.5")

    figures_dir = out_dir / "figures"
    results_dir = out_dir / "results"
    figures_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 3, figsize=(9, 6))
    mats = [
        rho_b_before,
        rho_b_uncond_z,
        rho_b_cond_z[0],
        rho_b_before,
        rho_b_uncond_x,
        rho_b_cond_x[0],
    ]
    titles = [
        "B before",
        "B uncond Z",
        "B cond Z (0)",
        "B before",
        "B uncond X",
        "B cond X (+)",
    ]
    for ax, mat, title in zip(axes.flat, mats, titles):
        ax.imshow(mat.real, vmin=-0.5, vmax=0.5, cmap="coolwarm")
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])
    plt.tight_layout()
    plt.savefig(figures_dir / "no_signalling_epr.png", dpi=150)
    plt.close(fig)

    payload = {
        "model": "bell_no_signalling_vs_conditioning",
        "no_signalling_dist_Z": float(no_sig_z),
        "no_signalling_dist_X": float(no_sig_x),
        "cond_outcome_dist_Z": float(cond_dist_z),
        "cond_outcome_dist_X": float(cond_dist_x),
        "p0_Z": float(p0_z),
        "p1_Z": float(p1_z),
        "p_plus_X": float(p_plus_x),
        "p_minus_X": float(p_minus_x),
    }

    json_path = results_dir / "no_signalling_epr.json"
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
