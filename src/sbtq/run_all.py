"""Run all experiments and generate a deterministic manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from sbtq.experiments.registry import get_experiments


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _build_manifest(out_dir: Path, artifacts: list[str]) -> dict:
    files = []
    for rel in artifacts:
        path = out_dir / rel
        files.append({"path": rel, "sha256": _sha256_file(path)})
    files_sorted = sorted(files, key=lambda x: x["path"])
    return {"files": files_sorted}


def _first_diff_path(old_files: list[dict], new_files: list[dict]) -> str:
    old_map = {f["path"]: f["sha256"] for f in old_files}
    new_map = {f["path"]: f["sha256"] for f in new_files}
    all_paths = sorted(set(old_map) | set(new_map))
    for path in all_paths:
        if old_map.get(path) != new_map.get(path):
            return path
    return "<unknown>"


def run_all(out_dir: Path, seed: int, check_existing: bool) -> None:
    experiments = get_experiments()

    old_manifest = None
    manifest_path = out_dir / "results" / "run_all_manifest.json"
    if check_existing and manifest_path.exists():
        old_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = {"seed": seed, "out": str(out_dir), "experiments": {}}
    all_artifacts: list[str] = []

    for exp in experiments:
        result = exp.run(out_dir=out_dir, seed=seed)
        metrics["experiments"][exp.name] = result
        all_artifacts.extend(exp.artifacts)

    results_dir = out_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    run_all_path = results_dir / "run_all.json"
    run_all_path.write_text(json.dumps(metrics, sort_keys=True, indent=2), encoding="utf-8")

    all_artifacts.append("results/run_all.json")
    manifest = _build_manifest(out_dir, all_artifacts)

    if old_manifest is not None and old_manifest != manifest:
        diff_path = _first_diff_path(old_manifest.get("files", []), manifest.get("files", []))
        raise AssertionError(f"Manifest mismatch at {diff_path}.")

    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("artifacts"))
    parser.add_argument("--check-existing", action="store_true")
    args = parser.parse_args()
    run_all(args.out, seed=args.seed, check_existing=args.check_existing)


if __name__ == "__main__":
    main()
