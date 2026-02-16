from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from sbtq.experiments import (
    cat_packaging,
    dephase_contexts,
    double_slit,
    markov_packaging,
    no_signalling_epr,
    quantum_eraser,
    route_mismatch,
)


@dataclass(frozen=True)
class Experiment:
    name: str
    entrypoint: str
    run: Callable[[Path, int], dict]
    artifacts: list[str]


def get_experiments() -> list[Experiment]:
    return [
        Experiment(
            name=double_slit.EXPERIMENT_NAME,
            entrypoint="sbtq.experiments.double_slit",
            run=double_slit.run,
            artifacts=double_slit.ARTIFACTS,
        ),
        Experiment(
            name=quantum_eraser.EXPERIMENT_NAME,
            entrypoint="sbtq.experiments.quantum_eraser",
            run=quantum_eraser.run,
            artifacts=quantum_eraser.ARTIFACTS,
        ),
        Experiment(
            name=route_mismatch.EXPERIMENT_NAME,
            entrypoint="sbtq.experiments.route_mismatch",
            run=route_mismatch.run,
            artifacts=route_mismatch.ARTIFACTS,
        ),
        Experiment(
            name=dephase_contexts.EXPERIMENT_NAME,
            entrypoint="sbtq.experiments.dephase_contexts",
            run=dephase_contexts.run,
            artifacts=dephase_contexts.ARTIFACTS,
        ),
        Experiment(
            name=no_signalling_epr.EXPERIMENT_NAME,
            entrypoint="sbtq.experiments.no_signalling_epr",
            run=no_signalling_epr.run,
            artifacts=no_signalling_epr.ARTIFACTS,
        ),
        Experiment(
            name=cat_packaging.EXPERIMENT_NAME,
            entrypoint="sbtq.experiments.cat_packaging",
            run=cat_packaging.run,
            artifacts=cat_packaging.ARTIFACTS,
        ),
        Experiment(
            name=markov_packaging.EXPERIMENT_NAME,
            entrypoint="sbtq.experiments.markov_packaging",
            run=markov_packaging.run,
            artifacts=markov_packaging.ARTIFACTS,
        ),
    ]
