# Cache

[← README](../README.md)

Tested with a 2-trial study, comparing `.dvc/cache` before and after.

| Added per trial | Where |
| --- | --- |
| `model/model.joblib` | `.dvc/cache/files` |
| `metrics/valid.json`, `metrics/test.json` | `.dvc/cache/files` |
| One run-cache entry each for `train` and `evaluate` | `.dvc/cache/runs` |

`prepare` has no tuned parameters, so its CSVs are cached once, not per trial.

`dvc.yaml` sets the metrics files to `cache: false`, but the run cache stores them
anyway. `cache: false` doesn't stop the run cache copying them in.

Each `train` run-cache entry records the trial's exact parameters and the hashes
of the model and metrics it produced. Reproducing a previous trial's parameters
restores its outputs from the cache rather than retraining.
