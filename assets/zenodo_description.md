## A Six-Birds' Eye View of Quantum Theory: Operational Closure Semantics for Measurement, Contextuality, and Record Stability

**Author:** Ioannis Tsiokos (Automorph Inc.)

### Summary

This paper presents a reproducible computational framework — with Lean 4 mechanized proofs and deterministic Python simulations — that recasts quantum measurement, contextuality, and the measurement problem using operational semantics drawn from Six Birds Theory (SBT), a closure-based emergence calculus.

Standard presentations of quantum mechanics mix causal evolution with inferential state update, so "collapse," contextuality, and Schrodinger's cat are often treated as physical discontinuities or as evidence for surplus ontology. We separate these roles explicitly: causal substrate dynamics are distinguished from *packaging* (an idempotent closure operation that stabilizes record-level objects via a chosen record algebra).

### Key results

- **Dephasing as packaging:** Dephasing in a fixed record basis is an idempotent packaging map whose fixed points are exactly the diagonal (record-classical) states.
- **Route mismatch:** Mismatch between evolution and packaging is approximately zero when the Hamiltonian is diagonal in the record basis, but nonzero for generic Hamiltonians or incompatible record bases.
- **Double slit and quantum eraser:** Decreasing environment-record overlap continuously suppresses fringe visibility; conditioning in a quantum eraser restores complementary fringes.
- **Measurement and the cat:** In a system-apparatus-environment model, the global state can remain near-pure while the packaged record state is a classical mixture, and packaging remains idempotent.
- **Classical analogue:** A metastable Markov chain demonstrates timescale-dependent staged objecthood using the same packaging formalism.

### Mechanized proofs (Lean 4)

Structural lemmas are mechanized in Lean 4, including: Leibniz quotient factorization, saturation idempotence, dephasing fixed-point characterization, finite total-variation data-processing inequality, and certified noncommutation witnesses.

### Reproducibility

All figures and quoted numbers are generated deterministically:

```
python -m sbtq.run_all --seed 0 --out artifacts
cd lean/Sbtq && lake build
```

The Python simulation suite (`sbtq`) includes deterministic seeding, hash-traceable artifacts, and robustness sweeps over multiple seeds.

### Repository contents

- `src/sbtq/` — Python simulation package (double slit, quantum eraser, route mismatch, cat packaging, Markov packaging, no-signalling EPR)
- `lean/Sbtq/` — Lean 4 mechanized proofs
- `paper/` — LaTeX manuscript source
- `artifacts/` — Generated figures and results
- `tests/` — Test suite

### Related works

- [Six Birds: Foundations of Emergence Calculus](https://doi.org/10.5281/zenodo.18365949) — The foundational SBT framework
- [To Become a Stone with Six Birds: A Physics is A Theory](https://doi.org/10.5281/zenodo.18412131) — Cross-domain SBT instantiation

### License

CC-BY 4.0
