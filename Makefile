.PHONY: install test experiments clean
.PHONY: paper-assets paper

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

experiments:
	python -m sbtq.run_all --seed 0 --out artifacts

paper-assets:
	python -m sbtq.run_all --seed 0 --out artifacts --check-existing
	python paper/scripts/sync_figures.py --src artifacts/figures --dst paper/figures
	python paper/scripts/generate_metrics_tex.py --src artifacts/results/run_all.json --dst paper/generated/metrics.tex
	python paper/scripts/generate_robustness_table_tex.py --src artifacts/results/robustness_summary.json --dst paper/generated/robustness_table.tex

paper:
	python scripts/build_quantum_paper.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -f artifacts/logs/*
