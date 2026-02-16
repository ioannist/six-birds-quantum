"""Robustness sweep across multiple seeds."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from sbtq.experiments.registry import get_experiments
from sbtq.dslit import probability_with_overlap, screen_grid, toy_amplitudes
from sbtq.eraser import conditional_path_states_pm, marked_joint_density
from sbtq.gates import basis_ket, cnot_matrix, pure_density
from sbtq.markov import E_tau, lens_two_basin, make_two_basin_chain, prototype_uniform
from sbtq.quantum import (
    apply_unitary,
    dephase,
    is_density_matrix,
    partial_dephase,
    partial_trace,
    random_density,
    trace_distance,
    unitary_from_hermitian,
)


def _is_finite_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _ensure_jsonable(obj: Any) -> None:
    json.dumps(obj)


def _add_range(ranges: dict[str, dict[str, float]], key: str, values: list[float]) -> None:
    ranges[key] = {
        "min": float(min(values)),
        "median": _median(values),
        "max": float(max(values)),
    }


def _record_value(values: dict[str, list[float]], key: str, val: float) -> None:
    values.setdefault(key, []).append(float(val))


def _sanity_density_matrices(anomalies: list[str], seed: int) -> None:
    rho_joint = marked_joint_density()
    states = conditional_path_states_pm(rho_joint)
    for name in ["rho_path_plus", "rho_path_minus", "rho_path_unconditional"]:
        rho = states[name]
        if not is_density_matrix(rho, tol=1e-10):
            anomalies.append(f"quantum_eraser: {name} not density matrix (seed={seed})")

    # Cat packaging states
    ket_plus = (basis_ket(1, 0) + basis_ket(1, 1)) / np.sqrt(2.0)
    ket0 = basis_ket(1, 0)
    psi = np.kron(np.kron(ket_plus, ket0), ket0)
    rho_init = pure_density(psi)

    cnot_sa = cnot_matrix(3, control=0, target=1)
    cnot_ae = cnot_matrix(3, control=1, target=2)

    rho_after_measure = cnot_sa @ rho_init @ cnot_sa.conj().T
    rho_sae = cnot_ae @ rho_after_measure @ cnot_ae.conj().T
    rho_sa_after = partial_trace(rho_sae, dims=[2, 2, 2], keep=[0, 1])
    rho_sa_packaged = dephase(rho_sa_after)

    for name, rho in [
        ("rho_SAE", rho_sae),
        ("rho_SA_after_record", rho_sa_after),
        ("rho_SA_packaged", rho_sa_packaged),
    ]:
        if not is_density_matrix(rho, tol=1e-10):
            anomalies.append(f"cat_packaging: {name} not density matrix (seed={seed})")

    # Route mismatch density checks for p=1
    d = 3
    base_seed = 123 + seed
    rng = np.random.default_rng(base_seed)
    x = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    h_rand = (x + x.conj().T) / 2.0
    rho = random_density(d=d, seed=base_seed + 1)
    for t in [0.1, 1.0, 2.0]:
        u = unitary_from_hermitian(h_rand, t)
        route1 = partial_dephase(apply_unitary(rho, u), 1.0)
        route2 = apply_unitary(partial_dephase(rho, 1.0), u)
        if not is_density_matrix(route1, tol=1e-10):
            anomalies.append(f"route_mismatch: route1 not density matrix (seed={seed}, t={t})")
        if not is_density_matrix(route2, tol=1e-10):
            anomalies.append(f"route_mismatch: route2 not density matrix (seed={seed}, t={t})")


def _sanity_probabilities(anomalies: list[str], seed: int) -> None:
    x = screen_grid()
    psi_a, psi_b = toy_amplitudes(x)
    for gamma in [1.0, 0.7, 0.3, 0.0]:
        p, _ = probability_with_overlap(psi_a, psi_b, gamma=gamma)
        if not np.all(np.isfinite(p)):
            anomalies.append(f"double_slit: non-finite P (seed={seed}, gamma={gamma})")
        if float(np.min(p)) < 0.0:
            anomalies.append(f"double_slit: negative P after clipping (seed={seed}, gamma={gamma})")

    # Markov: E_tau should be a valid distribution
    P = make_two_basin_chain()
    f = lens_two_basin(10)
    mu = prototype_uniform(10, 0)
    mu2 = E_tau(mu, P, f, 10, tau=1)
    if not np.isfinite(mu2).all():
        anomalies.append(f"markov: non-finite E_tau output (seed={seed})")
    if float(mu2.sum()) < 1.0 - 1e-8 or float(mu2.sum()) > 1.0 + 1e-8:
        anomalies.append(f"markov: E_tau sum not ~1 (seed={seed})")
    if float(mu2.min()) < -1e-12:
        anomalies.append(f"markov: E_tau has negative entries (seed={seed})")


def run_sweep(out_dir: Path, seeds: list[int]) -> dict:
    experiments = get_experiments()
    per_exp: dict[str, dict[str, Any]] = {}
    for exp in experiments:
        per_exp[exp.name] = {
            "runs": 0,
            "failures": 0,
            "ranges": {},
            "anomalies": [],
            "values": {},
        }
    separation_all = True

    for seed in seeds:
        anomalies: list[str] = []
        _sanity_density_matrices(anomalies, seed)
        _sanity_probabilities(anomalies, seed)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_out = Path(tmp_dir)
            for exp in experiments:
                info = per_exp[exp.name]
                info["runs"] += 1
                try:
                    metrics = exp.run(out_dir=tmp_out, seed=seed)
                    _ensure_jsonable(metrics)
                except Exception as exc:  # noqa: BLE001
                    info["failures"] += 1
                    info["anomalies"].append(f"seed={seed}: {type(exc).__name__}: {exc}")
                    continue

                if exp.name == "double_slit":
                    vis = metrics.get("visibility")
                    v0 = metrics.get("visibility_at_zero_gamma")
                    if not isinstance(vis, list) or len(vis) != 4:
                        info["failures"] += 1
                        info["anomalies"].append(f"seed={seed}: visibility list missing/length != 4")
                        continue
                    if not _is_finite_number(v0):
                        info["failures"] += 1
                        info["anomalies"].append(f"seed={seed}: visibility_at_zero_gamma invalid")
                        continue
                    for i, v in enumerate(vis):
                        if not _is_finite_number(v) or v < -1e-12 or v > 1.0 + 1e-6:
                            info["anomalies"].append(f"seed={seed}: visibility[{i}] out of range")
                    _record_value(info["values"], "visibility_at_zero_gamma", float(v0))
                    for i, v in enumerate(vis):
                        _record_value(info["values"], f"visibility[{i}]", float(v))

                elif exp.name == "quantum_eraser":
                    keys = [
                        "visibility_unconditional",
                        "visibility_plus",
                        "visibility_minus",
                        "fringe_anticorrelation",
                        "p_plus",
                        "p_minus",
                    ]
                    if any(k not in metrics for k in keys):
                        info["failures"] += 1
                        info["anomalies"].append(f"seed={seed}: missing keys")
                        continue
                    v_un = float(metrics["visibility_unconditional"])
                    v_p = float(metrics["visibility_plus"])
                    v_m = float(metrics["visibility_minus"])
                    corr = float(metrics["fringe_anticorrelation"])
                    p_plus = float(metrics["p_plus"])
                    p_minus = float(metrics["p_minus"])
                    for v in [v_un, v_p, v_m]:
                        if not _is_finite_number(v) or v < -1e-12 or v > 1.0 + 1e-6:
                            info["anomalies"].append(f"seed={seed}: visibility out of range")
                    if not _is_finite_number(corr) or corr < -1.0 - 1e-6 or corr > 1.0 + 1e-6:
                        info["anomalies"].append(f"seed={seed}: anticorrelation out of range")
                    if p_plus < -1e-12 or p_plus > 1.0 + 1e-12:
                        info["anomalies"].append(f"seed={seed}: p_plus out of range")
                    if p_minus < -1e-12 or p_minus > 1.0 + 1e-12:
                        info["anomalies"].append(f"seed={seed}: p_minus out of range")
                    if abs((p_plus + p_minus) - 1.0) > 1e-12:
                        info["anomalies"].append(f"seed={seed}: p_plus+p_minus != 1")
                    _record_value(info["values"], "visibility_unconditional", v_un)
                    _record_value(info["values"], "visibility_plus", v_p)
                    _record_value(info["values"], "visibility_minus", v_m)
                    _record_value(info["values"], "fringe_anticorrelation", corr)
                    _record_value(info["values"], "p_plus", p_plus)
                    _record_value(info["values"], "p_minus", p_minus)

                elif exp.name == "route_mismatch":
                    keys = [
                        "max_mismatch_random_H",
                        "max_mismatch_diagonal_H",
                        "max_heat_p0",
                    ]
                    if any(k not in metrics for k in keys):
                        info["failures"] += 1
                        info["anomalies"].append(f"seed={seed}: missing keys")
                        continue
                    max_rand = float(metrics["max_mismatch_random_H"])
                    max_diag = float(metrics["max_mismatch_diagonal_H"])
                    max_p0 = float(metrics["max_heat_p0"])
                    for v in [max_rand, max_diag, max_p0]:
                        if not _is_finite_number(v) or v < -1e-12:
                            info["anomalies"].append(f"seed={seed}: mismatch not finite/nonnegative")
                    if not (max_rand > 1e-3 and max_diag < 1e-10 and max_p0 < 1e-10):
                        separation_all = False
                        info["anomalies"].append(f"seed={seed}: separation check failed")
                    _record_value(info["values"], "max_mismatch_random_H", max_rand)
                    _record_value(info["values"], "max_mismatch_diagonal_H", max_diag)
                    _record_value(info["values"], "max_heat_p0", max_p0)

                elif exp.name == "dephase_contexts":
                    keys = ["mismatch_Z_tilt", "mismatch_ZX", "distance_to_maxmix_monotone"]
                    if any(k not in metrics for k in keys):
                        info["failures"] += 1
                        info["anomalies"].append(f"seed={seed}: missing keys")
                        continue
                    mismatch_tilt = float(metrics["mismatch_Z_tilt"])
                    mismatch_zx = float(metrics["mismatch_ZX"])
                    monotone = bool(metrics["distance_to_maxmix_monotone"])
                    distances = metrics.get("distance_to_maxmix", [])
                    if not _is_finite_number(mismatch_tilt) or mismatch_tilt < 0.0:
                        info["anomalies"].append(f"seed={seed}: mismatch_Z_tilt invalid")
                    if not _is_finite_number(mismatch_zx) or mismatch_zx < 0.0:
                        info["anomalies"].append(f"seed={seed}: mismatch_ZX invalid")
                    if mismatch_tilt <= 1e-3:
                        info["anomalies"].append(f"seed={seed}: mismatch_Z_tilt too small")
                    if mismatch_zx >= 1e-10:
                        info["anomalies"].append(f"seed={seed}: mismatch_ZX too large")
                    if not monotone:
                        info["anomalies"].append(f"seed={seed}: distance_to_maxmix not monotone")
                    if isinstance(distances, list) and distances:
                        final_dist = float(distances[-1])
                        if _is_finite_number(final_dist):
                            _record_value(info["values"], "distance_to_maxmix_final", final_dist)
                    _record_value(info["values"], "mismatch_Z_tilt", mismatch_tilt)
                    _record_value(info["values"], "mismatch_ZX", mismatch_zx)

                elif exp.name == "no_signalling_epr":
                    keys = [
                        "no_signalling_dist_Z",
                        "no_signalling_dist_X",
                        "cond_outcome_dist_Z",
                        "cond_outcome_dist_X",
                        "p0_Z",
                        "p1_Z",
                        "p_plus_X",
                        "p_minus_X",
                    ]
                    if any(k not in metrics for k in keys):
                        info["failures"] += 1
                        info["anomalies"].append(f"seed={seed}: missing keys")
                        continue
                    no_sig_z = float(metrics["no_signalling_dist_Z"])
                    no_sig_x = float(metrics["no_signalling_dist_X"])
                    cond_z = float(metrics["cond_outcome_dist_Z"])
                    cond_x = float(metrics["cond_outcome_dist_X"])
                    p0_z = float(metrics["p0_Z"])
                    p1_z = float(metrics["p1_Z"])
                    p_plus = float(metrics["p_plus_X"])
                    p_minus = float(metrics["p_minus_X"])
                    for v in [no_sig_z, no_sig_x, cond_z, cond_x]:
                        if not _is_finite_number(v) or v < -1e-12:
                            info["anomalies"].append(f"seed={seed}: no_signalling values invalid")
                    if no_sig_z > 1e-12 or no_sig_x > 1e-12:
                        info["anomalies"].append(f"seed={seed}: no_signalling too large")
                    if cond_z < 0.9 or cond_x < 0.9:
                        info["anomalies"].append(f"seed={seed}: conditional distance too small")
                    for p in [p0_z, p1_z, p_plus, p_minus]:
                        if p < -1e-12 or p > 1.0 + 1e-12:
                            info["anomalies"].append(f"seed={seed}: probability out of range")
                        if abs(p - 0.5) > 1e-12:
                            info["anomalies"].append(f"seed={seed}: probability not ~0.5")
                    _record_value(info["values"], "no_signalling_dist_Z", no_sig_z)
                    _record_value(info["values"], "no_signalling_dist_X", no_sig_x)
                    _record_value(info["values"], "cond_outcome_dist_Z", cond_z)
                    _record_value(info["values"], "cond_outcome_dist_X", cond_x)

                elif exp.name == "cat_packaging":
                    keys = [
                        "purity_SA_before_record",
                        "purity_SAE_after_record",
                        "purity_SA_after_record",
                        "dist_pack_vs_env",
                        "dist_pack_vs_mix",
                        "idempotence_error",
                    ]
                    if any(k not in metrics for k in keys):
                        info["failures"] += 1
                        info["anomalies"].append(f"seed={seed}: missing keys")
                        continue
                    for k in keys:
                        v = float(metrics[k])
                        if not _is_finite_number(v):
                            info["anomalies"].append(f"seed={seed}: {k} not finite")
                        if k.startswith("purity") or k.startswith("dist") or k == "idempotence_error":
                            if v < -1e-12 or v > 1.0 + 1e-6:
                                info["anomalies"].append(f"seed={seed}: {k} out of range")
                        _record_value(info["values"], k, v)

                elif exp.name == "markov_packaging":
                    keys = ["taus", "delta", "prototype_stability_max", "tau_first_stable"]
                    if any(k not in metrics for k in keys):
                        info["failures"] += 1
                        info["anomalies"].append(f"seed={seed}: missing keys")
                        continue
                    taus = metrics["taus"]
                    delta = metrics["delta"]
                    stability = metrics["prototype_stability_max"]
                    if not isinstance(taus, list) or not isinstance(delta, list) or not isinstance(stability, list):
                        info["failures"] += 1
                        info["anomalies"].append(f"seed={seed}: taus/delta/stability not lists")
                        continue
                    if len(taus) != len(delta) or len(taus) != len(stability):
                        info["anomalies"].append(f"seed={seed}: list length mismatch")
                    for i, v in enumerate(delta):
                        if not _is_finite_number(v) or v < -1e-12 or v > 1.0 + 1e-6:
                            info["anomalies"].append(f"seed={seed}: delta[{i}] out of range")
                    for i, v in enumerate(stability):
                        if not _is_finite_number(v) or v < -1e-12 or v > 1.0 + 1e-6:
                            info["anomalies"].append(f"seed={seed}: stability[{i}] out of range")
                    tau_first = metrics["tau_first_stable"]
                    if tau_first is not None and not isinstance(tau_first, int):
                        info["anomalies"].append(f"seed={seed}: tau_first_stable not int/None")
                    _record_value(info["values"], "tau_first_stable", float(tau_first) if tau_first is not None else float("nan"))
                    for i, v in enumerate(delta):
                        _record_value(info["values"], f"delta[{i}]", float(v))
                    for i, v in enumerate(stability):
                        _record_value(info["values"], f"prototype_stability_max[{i}]", float(v))

                else:
                    info["anomalies"].append(f"seed={seed}: unknown experiment {exp.name}")

        if anomalies:
            for exp in experiments:
                per_exp[exp.name]["anomalies"].extend(anomalies)

    summary = {
        "seeds": seeds,
        "experiments": {},
        "overall_ok": True,
    }

    for name, info in per_exp.items():
        ranges: dict[str, dict[str, float]] = {}
        for key, vals in info["values"].items():
            if any(not _is_finite_number(v) for v in vals):
                info["anomalies"].append(f"non-finite values for {key}")
                continue
            _add_range(ranges, key, [float(v) for v in vals])
        payload = {
            "runs": info["runs"],
            "failures": info["failures"],
            "ranges": ranges,
            "anomalies": info["anomalies"],
        }
        if name == "route_mismatch":
            payload["separation_all_seeds"] = separation_all
        summary["experiments"][name] = payload

    if any(info["failures"] > 0 or info["anomalies"] for info in per_exp.values()):
        summary["overall_ok"] = False
    if not separation_all:
        summary["overall_ok"] = False

    out_dir.mkdir(parents=True, exist_ok=True)
    results_dir = out_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / "robustness_summary.json"
    out_path.write_text(json.dumps(summary, sort_keys=True, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("artifacts"))
    parser.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    args = parser.parse_args()
    run_sweep(args.out, seeds=list(args.seeds))


if __name__ == "__main__":
    main()
