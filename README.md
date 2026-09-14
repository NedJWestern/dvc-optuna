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

`src/tune.py` runs an Optuna study over that pipeline. Each trial writes its
sampled values into `params.yaml` and calls `Repo.reproduce()` in-process, so DVC
re-runs only the affected stages and the objective is read from the metrics file
that stage produced. The committed parameters are restored when the study ends,
including on `Ctrl-C`.

```bash
uv run python src/tune.py
```

No DVC experiment is recorded per trial. Optuna's storage holds the study, and
the run prints the `dvc exp run -S ...` command that replays the best trial and
records it as an experiment.

The search is declared in `search.yaml`, kept separate from `params.yaml` so
that editing a sweep can never look like a change to a stage's inputs.

| Field | Meaning |
| --- | --- |
| `space` keys | Dotted DVC parameter paths, written straight into `params.yaml` |
| `space` values | A `trial.suggest_*` call — `type` picks the method, the remaining keys are forwarded as keyword arguments |
| `objective.metric` | `<metrics file>:<dotted key>` |
| `objective.direction` | `minimize` or `maximize` |
| `storage` | Optuna storage URL. This is the only record of the study, so it also makes a study resumable — trial numbering continues rather than restarting |

Anything Optuna accepts (`log`, `step`, `choices`) therefore works without
touching `tune.py`.

## Limits

| Limit | Detail |
| --- | --- |
| Per-trial overhead | ~1.4s of DVC bookkeeping on top of the stages themselves, which is significant when a stage runs as quickly as this one |
| Pruning | Unavailable — a stage is an opaque subprocess, so there is no intermediate value to report back to Optuna |
| Workspace | Trials run in the working tree, so `params.yaml`, `metrics/` and `dvc.lock` all churn for the duration of a study |
| Validation size | 360 rows, small enough for a long study to start fitting the split itself |

That last one is not hypothetical. A 25-trial study improved validation logloss
from 0.0865 to 0.0673, but its best trial scored *worse* on the test split than
the untuned baseline — 0.174 against 0.138. Cross-validating inside the train
stage would fix it, at roughly 5× the cost per trial.
