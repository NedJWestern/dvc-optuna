# dvc-optuna

A minimal scikit-learn project whose training pipeline is managed by [DVC](https://dvc.org/)
and tuned by an [Optuna](https://optuna.org/) study.

## Setup

```bash
uv sync
```

## Data

UCI *Optical Recognition of Handwritten Digits*, shipped with scikit-learn:
1797 samples, 64 features, 10 classes. Nothing is downloaded.

## Pipeline

`prepare` → `train` → `evaluate`, defined in `dvc.yaml`.

| Stage | Script | Outputs |
| --- | --- | --- |
| `prepare` | `src/prepare.py` | `data/{train,valid,test}.csv` |
| `train` | `src/train.py` | `model/model.joblib`, `metrics/valid.json` |
| `evaluate` | `src/evaluate.py` | `metrics/test.json` |

The model is a `HistGradientBoostingClassifier`. Its hyperparameters live in
`params.yaml`, so DVC re-runs only the stages a change actually affects.
`metrics/valid.json` is the tuning signal; `metrics/test.json` comes from the
held-out split and should only be read once a configuration has been chosen.

```bash
uv run dvc repro          # run the pipeline
uv run dvc metrics show   # current metrics
uv run dvc exp show       # compare experiments
```

## Tuning

`src/tune.py` runs an Optuna study over that pipeline. Each trial passes its
sampled values to `dvc exp run -S`: DVC writes them into `params.yaml`, re-runs
only the affected stages, and records the result as a named experiment. The
objective is then read back out of the metrics file the pipeline produced.

```bash
uv run python src/tune.py
uv run dvc exp apply digits-tpe-024   # adopt a trial's parameters
```

The search is declared in `search.yaml`, kept separate from `params.yaml` so
that editing a sweep can never look like a change to a stage's inputs.

| Field | Meaning |
| --- | --- |
| `space` keys | Dotted DVC parameter paths, passed straight through to `-S` |
| `space` values | A `trial.suggest_*` call — `type` picks the method, the remaining keys are forwarded as keyword arguments |
| `objective.metric` | `<metrics file>:<dotted key>` |
| `objective.direction` | `minimize` or `maximize` |
| `storage` | Optional Optuna storage URL; set it to make a study resumable |

Anything Optuna accepts (`log`, `step`, `choices`) therefore works without
touching `tune.py`.

## Limits

| Limit | Detail |
| --- | --- |
| Per-trial overhead | A few seconds of git and hashing, which dominates when a stage runs as quickly as this one |
| Pruning | Unavailable — a trial is an opaque subprocess, so there is no intermediate value to report back to Optuna |
| Validation size | 360 rows, small enough for a long study to start fitting the split itself |

That last one is not hypothetical. A 25-trial study improved validation logloss
from 0.0865 to 0.0673, but its best trial scored *worse* on the test split than
the untuned baseline — 0.174 against 0.138. Cross-validating inside the train
stage would fix it, at roughly 5× the cost per trial.
