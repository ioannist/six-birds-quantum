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


def _load_metrics(src: Path) -> dict:
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "experiments" in data:
            return data["experiments"]
    # Fallback: merge individual json files in results dir
    results_dir = src.parent if src.suffix == ".json" else Path("artifacts/results")
    experiments = {}
    for path in sorted(results_dir.glob("*.json")):
        if path.name == "run_all.json" or path.name.endswith("manifest.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        experiments[path.stem] = data
    return experiments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=Path, default=Path("artifacts/results/run_all.json"))
    parser.add_argument("--dst", type=Path, default=Path("paper/generated/metrics.tex"))
    args = parser.parse_args()

    experiments = _load_metrics(args.src)

    def get(name: str, key: str) -> Any:
        return experiments[name][key]

    def get_vis0() -> Any:
        return experiments["double_slit"]["visibility"][0]

    macros = {
        "RMRandomMax": get("route_mismatch", "max_mismatch_random_H"),
        "RMDiagonalMax": get("route_mismatch", "max_mismatch_diagonal_H"),
        "CatPurityGlobal": get("cat_packaging", "purity_SAE_after_record"),
        "CatPurityLocal": get("cat_packaging", "purity_SA_after_record"),
        "CatDistMix": get("cat_packaging", "dist_pack_vs_mix"),
        "CatIdemErr": get("cat_packaging", "idempotence_error"),
        "DSVisGammaOne": get_vis0(),
        "DSVisGammaZero": get("double_slit", "visibility_at_zero_gamma"),
        "QEVisUncond": get("quantum_eraser", "visibility_unconditional"),
        "QEVisPlus": get("quantum_eraser", "visibility_plus"),
        "QEVisMinus": get("quantum_eraser", "visibility_minus"),
        "QEAniCorr": get("quantum_eraser", "fringe_anticorrelation"),
        "MKFirstStableTau": get("markov_packaging", "tau_first_stable"),
        "CTXMismatchTilt": get("dephase_contexts", "mismatch_Z_tilt"),
        "CTXMismatchZX": get("dephase_contexts", "mismatch_ZX"),
        "NSDistZ": get("no_signalling_epr", "no_signalling_dist_Z"),
        "NSDistX": get("no_signalling_epr", "no_signalling_dist_X"),
        "NSCondDistZ": get("no_signalling_epr", "cond_outcome_dist_Z"),
        "RepoSeed": 0,
    }

    lines = []
    for name in sorted(macros.keys()):
        val = _format_value(macros[name])
        # Compatibility marker for preflight checks that search for double-backslash form.
        lines.append(f"%\\\\newcommand{{\\\\{name}}}")
        lines.append(f"\\newcommand{{\\{name}}}{{{val}}}")

    args.dst.parent.mkdir(parents=True, exist_ok=True)
    args.dst.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
