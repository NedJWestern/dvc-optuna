# Limits

[← README](../README.md)

| Limit | Detail |
| --- | --- |
| Per-trial overhead | ~1.4s of DVC bookkeeping on top of the stages themselves, which is significant when a stage runs as quickly as this one |
| Pruning | Unavailable. A stage is an opaque subprocess, so there is no intermediate value to report back to Optuna |
| Workspace | Trials run in the working tree, so `params.yaml`, `metrics/` and `dvc.lock` all churn for the duration of a study |
| Validation size | 360 rows, small enough for a long study to start fitting the split itself |
| Test metrics | `evaluate` runs in every trial and its results are cached, so `metrics/test.json` can be read before a configuration is chosen |

## Overfitting the validation split

`metrics/valid.json` is the tuning signal. `metrics/test.json` comes from the
held-out split and should only be read once a configuration has been chosen.

The validation-size limit shows up in practice. A 25-trial study improved validation
logloss from 0.0865 to 0.0673, but its best trial scored *worse* on the test split
than the untuned baseline: 0.174 against 0.138. Cross-validating inside the train
stage would fix it, at roughly 5× the cost per trial.
