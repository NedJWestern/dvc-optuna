"""Drive the DVC pipeline from an Optuna study.

Each trial hands its sampled values to `dvc exp run -S`, which writes them into
params.yaml, re-runs only the stages those parameters affect, and records the
result as a named DVC experiment. The objective is then read back out of the
metrics file the pipeline just produced.

DVC owns reproducibility and caching; Optuna owns the search. Neither needs to
know anything about the other beyond the parameter names in search.yaml.
"""

import json
import subprocess
from pathlib import Path

import optuna
import yaml

SEARCH_FILE = Path("search.yaml")
PARAMS_FILE = Path("params.yaml")


def suggest(trial: optuna.Trial, name: str, spec: dict):
    """Turn one search.yaml entry into the trial.suggest_* call it describes."""
    spec = dict(spec)
    kind = spec.pop("type")
    return getattr(trial, f"suggest_{kind}")(name, **spec)


def as_flag(value) -> str:
    """Render a sampled value the way `dvc exp run -S` expects to read it."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def read_metric(address: str) -> float:
    """Read `path/to/file.json:dotted.key` out of the workspace."""
    path, _, key = address.rpartition(":")
    value = json.loads(Path(path).read_text())
    for part in key.split("."):
        value = value[part]
    return float(value)


def run_experiment(name: str, params: dict) -> None:
    cmd = ["dvc", "exp", "run", "--quiet", "--name", name]
    for key, value in params.items():
        cmd += ["--set-param", f"{key}={as_flag(value)}"]
    subprocess.run(cmd, check=True)


def main() -> None:
    config = yaml.safe_load(SEARCH_FILE.read_text())
    space = config["space"]
    metric = config["objective"]["metric"]
    study_name = config["study_name"]

    def objective(trial: optuna.Trial) -> float:
        params = {name: suggest(trial, name, spec) for name, spec in space.items()}
        name = f"{study_name}-{trial.number:03d}"
        run_experiment(name, params)
        trial.set_user_attr("dvc_exp", name)
        return read_metric(metric)

    study = optuna.create_study(
        study_name=study_name,
        direction=config["objective"]["direction"],
        sampler=optuna.samplers.TPESampler(seed=config.get("seed")),
        storage=config.get("storage"),
        load_if_exists=True,
    )

    # `dvc exp run` edits params.yaml in place and leaves the last trial's values
    # behind, so put the committed ones back whatever happens.
    baseline = PARAMS_FILE.read_bytes()
    try:
        study.optimize(
            objective,
            n_trials=config["n_trials"],
            catch=(subprocess.CalledProcessError,),
        )
    finally:
        PARAMS_FILE.write_bytes(baseline)
        subprocess.run(["dvc", "repro", "--quiet"], check=False)

    best = study.best_trial
    print(f"\nbest trial: {best.user_attrs['dvc_exp']}  ({metric} = {best.value:.5f})")
    for key, value in best.params.items():
        print(f"  {key}: {value}")
    print(f"\nadopt it with:  dvc exp apply {best.user_attrs['dvc_exp']}")


if __name__ == "__main__":
    main()
