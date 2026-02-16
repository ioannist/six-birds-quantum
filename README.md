# A Six-Birds' Eye View of Quantum Theory

> **A Six-Birds' Eye View of Quantum Theory: Operational Closure Semantics for Measurement, Contextuality, and Record Stability**
>
> Archived at: https://zenodo.org/records/TBD
>
> DOI: https://doi.org/10.5281/zenodo.TBD

This paper recasts finite-dimensional quantum mechanics in the Six Birds Theory (SBT) language of packaging, closures, and audits. It separates causal substrate evolution from record-level packaging, and supports the narrative with mechanized structural lemmas (Lean) and reproducible experiments.

## What this repository provides

- **Core quantum primitives**: density-matrix helpers, dephasing/partial trace, trace distance
- **Packaging/closure diagnostics**: idempotence, route mismatch, fixed points
- **Canonical experiments**: double slit + eraser, route mismatch, cat packaging, Markov analogue, incompatible dephasing contexts, EPR no-signalling vs conditioning
- **Deterministic experiment runner**: `run_all` with manifest-based determinism checks
- **Robustness sweep**: 10-seed sanity checks with min/median/max summary
- **Lean mechanization**: quotient/closure/audit lemmas and finite witnesses
- **Paper build pipeline**: figures + metrics generated from repo artifacts

## Scope and limitations

- No new quantum microdynamics are proposed; standard CPTP/unitary evolution is assumed.
- Packaging is an interpretational bookkeeping layer, not a new causal law.
- We do not claim to resolve Bell/PBR or derive the Born rule here.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cd lean && lake build
```

## Test

```bash
pytest -q
```

## Run experiments (canonical)

```bash
python -m sbtq.run_all --seed 0 --out artifacts
python -m sbtq.run_all --seed 0 --out artifacts --check-existing
python -m sbtq.robustness_sweep --out artifacts --seeds 0 1 2 3 4 5 6 7 8 9
```

## Build paper

```bash
make paper
```
