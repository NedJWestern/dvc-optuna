# dvc-optuna

A minimal scikit-learn project whose training pipeline is managed by [DVC](https://dvc.org/)
and tuned by an [Optuna](https://optuna.org/) study.

The data is scikit-learn's bundled UCI handwritten-digits set, so nothing is downloaded.

```bash
uv sync
uv run python src/tune.py
```

## Docs

| Doc | Covers |
| --- | --- |
| [Tuning](docs/tuning.md) | What a study run does and leaves behind |
| [Why the DVC Python API](docs/dvc-python-api.md) | Why trials call `Repo.reproduce()` rather than `dvc exp run` |
| [Cache](docs/cache.md) | What each trial stores in `.dvc/cache` |
| [Limits](docs/limits.md) | Known weaknesses of the approach |
