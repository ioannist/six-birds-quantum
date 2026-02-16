| Experiment | Entrypoint | Artifacts (relative to `--out`) |
| --- | --- | --- |
| double_slit | `python -m sbtq.experiments.double_slit` | `figures/double_slit_patterns.png`, `figures/double_slit_visibility.png`, `results/double_slit.json` |
| quantum_eraser | `python -m sbtq.experiments.quantum_eraser` | `figures/quantum_eraser_unconditional.png`, `figures/quantum_eraser_conditional.png`, `results/quantum_eraser.json` |
| route_mismatch | `python -m sbtq.experiments.route_mismatch` | `figures/route_mismatch_vs_time.png`, `figures/route_mismatch_heatmap.png`, `results/route_mismatch.json` |
| dephase_contexts | `python -m sbtq.experiments.dephase_contexts` | `figures/dephase_contexts_mismatch.png`, `results/dephase_contexts.json` |
| no_signalling_epr | `python -m sbtq.experiments.no_signalling_epr` | `figures/no_signalling_epr.png`, `results/no_signalling_epr.json` |
| cat_packaging | `python -m sbtq.experiments.cat_packaging` | `figures/cat_packaging.png`, `results/cat_packaging.json` |
| markov_packaging | `python -m sbtq.experiments.markov_packaging` | `figures/markov_idempotence_vs_tau.png`, `results/markov_packaging.json` |
