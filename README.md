# dvc-optuna

A minimal scikit-learn project whose training pipeline is managed by [DVC](https://dvc.org/),
built as a base for experimenting with [Optuna](https://optuna.org/) integration.

## Data

The UCI *Optical Recognition of Handwritten Digits* set, shipped with scikit-learn
(1797 samples, 64 features, 10 classes). No download step is needed.

## Pipeline

```
prepare  ->  train  ->  evaluate
```

| Stage | Script | Outputs |
| --- | --- | --- |
| `prepare` | `src/prepare.py` | `data/{train,valid,test}.csv` |
| `train` | `src/train.py` | `model/model.joblib`, `metrics/valid.json` |
| `evaluate` | `src/evaluate.py` | `metrics/test.json` |

The model is a `HistGradientBoostingClassifier`. All hyperparameters live in
`params.yaml`, so DVC re-runs only the stages a change actually affects.

`metrics/valid.json` is the tuning signal; `metrics/test.json` comes from the
held-out split and should only be read once a configuration has been chosen.

## Setup

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv -r requirements.txt
source .venv/bin/activate
```

## Usage

```bash
dvc repro                                  # run the pipeline
dvc metrics show                           # current metrics
dvc exp run -S train.learning_rate=0.05    # one-off experiment
dvc exp show                               # compare experiments
```

## Tuning

`src/tune.py` joins Optuna to the pipeline. Each trial hands its sampled values
to `dvc exp run -S`, so DVC writes them into `params.yaml`, re-runs only the
stages they affect, and records the result as a named experiment; the objective
is then read back out of the metrics file the pipeline produced.

```bash
python src/tune.py
dvc exp apply digits-tpe-024    # adopt a trial's parameters
```

The search lives in `search.yaml`, deliberately separate from `params.yaml` so
that editing the sweep can never look like a change to a stage's inputs:

```yaml
space:
  train.learning_rate: {type: float, low: 0.01, high: 0.5, log: true}
  train.max_iter:      {type: int, low: 50, high: 400, step: 50}
```

Keys are dotted DVC parameter paths, passed straight through to `-S`. Each value
is a `trial.suggest_*` call — `type` picks the method and the remaining keys are
forwarded as keyword arguments, so anything Optuna accepts works without
changing `tune.py`.

Two limits worth knowing. Trials cost a few seconds of git and hashing overhead
each, which dominates when a stage is as quick as this one. And pruning is not
available: a trial is an opaque subprocess, so there is no intermediate value to
report back to Optuna.
