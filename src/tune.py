"""Run an Optuna study over the DVC pipeline.

Each trial writes its sampled values into params.yaml and calls Repo.reproduce(),
so DVC re-runs only the stages those parameters affect and the objective is read
from the metrics file that stage produced.

No DVC experiment is recorded per trial: Optuna's storage is the record of the
study, and the best trial is replayed through `dvc exp run` once at the end.
"""

import json
from pathlib import Path

import optuna
import yaml
from dvc.exceptions import ReproductionError
from dvc.repo import Repo

SEARCH_FILE = Path("search.yaml")
PARAMS_FILE = Path("params.yaml")


def suggest(trial: optuna.Trial, name: str, spec: dict):
    """Turn one search.yaml entry into the trial.suggest_* call it describes."""
    spec = dict(spec)
    kind = spec.pop("type")
    return getattr(trial, f"suggest_{kind}")(name, **spec)


def write_params(values: dict) -> None:
    """Set dotted parameter paths in params.yaml, leaving the other keys alone."""
    params = yaml.safe_load(PARAMS_FILE.read_text())
    for dotted, value in values.items():
        *sections, key = dotted.split(".")
        target = params
        for section in sections:
            target = target[section]
        target[key] = value
    PARAMS_FILE.write_text(yaml.safe_dump(params, sort_keys=False))


def read_metric(address: str) -> float:
    """Read `path/to/file.json:dotted.key` out of the workspace."""
    path, _, key = address.rpartition(":")
    value = json.loads(Path(path).read_text())
    for part in key.split("."):
        value = value[part]
    return float(value)


def as_flag(value) -> str:
    """Render a sampled value the way `dvc exp run -S` expects to read it."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def main() -> None:
    config = yaml.safe_load(SEARCH_FILE.read_text())
    space = config["space"]
    metric = config["objective"]["metric"]

    study = optuna.create_study(
        study_name=config["study_name"],
        direction=config["objective"]["direction"],
        sampler=optuna.samplers.TPESampler(seed=config.get("seed")),
        storage=config.get("storage"),
        load_if_exists=True,
    )

    # reproduce() rewrites params.yaml's neighbours (metrics, dvc.lock) as it goes,
    # so put the committed parameters back and rebuild from them whatever happens.
    baseline = PARAMS_FILE.read_bytes()
    with Repo() as repo:

        def objective(trial: optuna.Trial) -> float:
            write_params({name: suggest(trial, name, spec) for name, spec in space.items()})
            repo.reproduce()
            return read_metric(metric)

        try:
            study.optimize(
                objective,
                n_trials=config["n_trials"],
                catch=(ReproductionError,),
            )
        finally:
            PARAMS_FILE.write_bytes(baseline)
            repo.reproduce()

    best = study.best_trial
    flags = " ".join(f"-S {name}={as_flag(value)}" for name, value in best.params.items())
    print(f"\nbest trial {best.number}: {metric} = {best.value:.5f}")
    for name, value in best.params.items():
        print(f"  {name}: {value}")
    print("\nrecord it as a DVC experiment with:")
    print(f"  uv run dvc exp run -n {config['study_name']}-best {flags}")


if __name__ == "__main__":
    main()
