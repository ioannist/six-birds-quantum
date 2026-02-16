# Paper Build

Generate artifacts deterministically:

- `python -m sbtq.run_all --seed 0 --out artifacts --check-existing`

Sync figures:

- `python paper/scripts/sync_figures.py --src artifacts/figures --dst paper/figures`

Generate metrics:

- `python paper/scripts/generate_metrics_tex.py --src artifacts/results/run_all.json --dst paper/generated/metrics.tex`

Build PDF (best effort):

- `latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=paper/build paper/main.tex`

Fallback:

- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=paper/build paper/main.tex` (run twice)
