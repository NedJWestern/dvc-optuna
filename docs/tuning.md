# Tuning

[← README](../README.md)

```bash
uv run python src/tune.py
```

`src/tune.py` runs an Optuna study over the pipeline, configured by `search.yaml`.

| When | What happens |
| --- | --- |
| Each trial | Sampled values are written into `params.yaml`, then `Repo.reproduce()` re-runs the affected stages |
| Study ends, including on `Ctrl-C` | The committed `params.yaml` is restored and the pipeline rebuilt from it |
| After the study | The best trial is printed, with the `dvc exp run -S ...` command that replays it as a DVC experiment |

## Where results live

The Optuna `storage` URL in `search.yaml` is the only record of the study. It also
makes a study resumable: trial numbering continues rather than restarting. No DVC
experiment is created per trial. See [Why the DVC Python API](dvc-python-api.md).

Each trial's model and metrics are still kept in DVC's run cache. See [Cache](cache.md).
