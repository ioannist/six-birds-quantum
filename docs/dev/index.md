# Commands

## Python runner
- `python -m sbtq.run_all --seed 0 --out artifacts`
- `python -m sbtq.run_all --seed 0 --out artifacts --check-existing`

## Individual experiments
- `python -m sbtq.experiments.double_slit --seed 0 --out artifacts`
- `python -m sbtq.experiments.quantum_eraser --seed 0 --out artifacts`
- `python -m sbtq.experiments.route_mismatch --seed 0 --out artifacts`
- `python -m sbtq.experiments.dephase_contexts --seed 0 --out artifacts`
- `python -m sbtq.experiments.no_signalling_epr --seed 0 --out artifacts`
- `python -m sbtq.experiments.cat_packaging --seed 0 --out artifacts`
- `python -m sbtq.experiments.markov_packaging --seed 0 --out artifacts`

## Lean build
- `cd lean/Sbtq && lake build`

# Experiment IDs

| ID | Name | Entrypoint | Code | Artifacts | Results JSON |
| --- | --- | --- | --- | --- | --- |
| EXP-DS1 | double slit overlap | `python -m sbtq.experiments.double_slit --seed 0 --out artifacts` | `src/sbtq/experiments/double_slit.py` | `figures/double_slit_patterns.png`, `figures/double_slit_visibility.png` | `results/double_slit.json` |
| EXP-QE1 | quantum eraser conditioning | `python -m sbtq.experiments.quantum_eraser --seed 0 --out artifacts` | `src/sbtq/experiments/quantum_eraser.py` | `figures/quantum_eraser_unconditional.png`, `figures/quantum_eraser_conditional.png` | `results/quantum_eraser.json` |
| EXP-RM1 | route mismatch dephase vs unitary | `python -m sbtq.experiments.route_mismatch --seed 0 --out artifacts` | `src/sbtq/experiments/route_mismatch.py` | `figures/route_mismatch_vs_time.png`, `figures/route_mismatch_heatmap.png` | `results/route_mismatch.json` |
| EXP-CTX1 | dephase contexts mismatch | `python -m sbtq.experiments.dephase_contexts --seed 0 --out artifacts` | `src/sbtq/experiments/dephase_contexts.py` | `figures/dephase_contexts_mismatch.png` | `results/dephase_contexts.json` |
| EXP-NS1 | no signalling EPR | `python -m sbtq.experiments.no_signalling_epr --seed 0 --out artifacts` | `src/sbtq/experiments/no_signalling_epr.py` | `figures/no_signalling_epr.png` | `results/no_signalling_epr.json` |
| EXP-CAT1 | cat packaging | `python -m sbtq.experiments.cat_packaging --seed 0 --out artifacts` | `src/sbtq/experiments/cat_packaging.py` | `figures/cat_packaging.png` | `results/cat_packaging.json` |
| EXP-MK1 | Markov packaging | `python -m sbtq.experiments.markov_packaging --seed 0 --out artifacts` | `src/sbtq/experiments/markov_packaging.py` | `figures/markov_idempotence_vs_tau.png` | `results/markov_packaging.json` |

# Lean theorem IDs

| ID | File | Symbols |
| --- | --- | --- |
| THM-LQ1 | `lean/Sbtq/Sbtq/LeibnizQuotient.lean` | `quotient_lift_exists_unique` |
| THM-LQ2 | `lean/Sbtq/Sbtq/LeibnizQuotient.lean` | `liftLens_comp_q` |
| THM-DEF1 | `lean/Sbtq/Sbtq/Definability.lean` | `definable_iff_constantOnFibers` |
| THM-DEF2 | `lean/Sbtq/Sbtq/Definability.lean` | `refines_original_iff_definable` |
| THM-DEF3 | `lean/Sbtq/Sbtq/Definability.lean` | `refined_strictlyRefines_of_notDefinable` |
| THM-PKG1 | `lean/Sbtq/Sbtq/PackagingFromEquivalence.lean` | `sat_idem` |
| THM-PKG2 | `lean/Sbtq/Sbtq/PackagingFromEquivalence.lean` | `sat_eq_iff_unionOfClasses` |
| THM-PKG3 | `lean/Sbtq/Sbtq/PackagingFromEquivalence.lean` | `sat_eq_iUnion_classOf` |
| THM-RM1 | `lean/Sbtq/Sbtq/RouteMismatch.lean` | `mismatch_witness` |
| THM-RM2 | `lean/Sbtq/Sbtq/RouteMismatch.lean` | `not_commute_E_F` |
| THM-QD1 | `lean/Sbtq/Sbtq/QuantumDephase.lean` | `dephase_idem` |
| THM-QD2 | `lean/Sbtq/Sbtq/QuantumDephase.lean` | `dephase_fixed_iff_exists_diagonal` |
| THM-DPI1 | `lean/Sbtq/Sbtq/DPI_Finite.lean` | `tvdist_pushforward_le` |
