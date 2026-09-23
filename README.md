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

## Tuning

`src/tune.py` runs an Optuna study over the pipeline, configured by `search.yaml`.
The committed parameters are restored when the study ends, including on `Ctrl-C`.

```bash
uv run python src/tune.py
```

The run ends by printing the `dvc exp run -S ...` command that replays the best
trial as a DVC experiment. The Optuna `storage` URL is the only record of the
study, and makes it resumable — trial numbering continues rather than restarting.

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
