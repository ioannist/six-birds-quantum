import argparse
import json
from pathlib import Path
from typing import Any


def _format_value(val: Any) -> str:
    if isinstance(val, bool):
        return "1" if val else "0"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return "{:.6g}".format(val)
    return str(val)


def _escape_tex(text: str) -> str:
    return text.replace("_", "\\_")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=Path, default=Path("artifacts/results/robustness_summary.json"))
    parser.add_argument("--dst", type=Path, default=Path("paper/generated/robustness_table.tex"))
    args = parser.parse_args()

    data = json.loads(args.src.read_text(encoding="utf-8"))
    experiments = data.get("experiments", {})

    order = [
        ("double_slit", ["visibility[0]", "visibility_at_zero_gamma"]),
        ("quantum_eraser", ["visibility_unconditional", "visibility_plus", "visibility_minus"]),
        ("route_mismatch", ["max_mismatch_random_H", "max_mismatch_diagonal_H"]),
        ("cat_packaging", ["purity_SAE_after_record", "purity_SA_after_record", "dist_pack_vs_mix", "idempotence_error"]),
        ("markov_packaging", ["tau_first_stable"]),
        ("dephase_contexts", ["mismatch_Z_tilt", "mismatch_ZX", "distance_to_maxmix_final"]),
        ("no_signalling_epr", ["no_signalling_dist_Z", "no_signalling_dist_X", "cond_outcome_dist_Z"]),
    ]

    rows = []
    for exp_name, metrics in order:
        exp = experiments.get(exp_name)
        if not exp:
            continue
        ranges = exp.get("ranges", {})
        for metric in metrics:
            if metric not in ranges:
                continue
            r = ranges[metric]
            if not isinstance(r, dict):
                continue
            if any(k not in r for k in ("min", "median", "max")):
                continue
            rows.append(
                (
                    exp_name,
                    metric,
                    _format_value(r["min"]),
                    _format_value(r["median"]),
                    _format_value(r["max"]),
                )
            )

    lines = []
    lines.append("\\begin{table}[t]")
    lines.append("  \\centering")
    lines.append("  \\begin{tabular}{l l r r r}")
    lines.append("    \\toprule")
    lines.append("    Experiment & Metric & Min & Median & Max \\\\")
    lines.append("    \\midrule")
    for exp_name, metric, vmin, vmed, vmax in rows:
        lines.append(
            f"    {_escape_tex(exp_name)} & {_escape_tex(metric)} & {vmin} & {vmed} & {vmax} \\\\"
        )
    lines.append("    \\bottomrule")
    lines.append("  \\end{tabular}")
    lines.append("  \\caption{Robustness sweep summary (min/median/max over seeds).}")
    lines.append("  \\label{tab:robustness-sweep}")
    lines.append("\\end{table}")

    args.dst.parent.mkdir(parents=True, exist_ok=True)
    args.dst.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
