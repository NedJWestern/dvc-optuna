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
dvc repro                              # run the pipeline
dvc metrics show                       # current metrics
dvc exp run -S train.learning_rate=0.05    # one-off experiment
dvc exp show                           # compare experiments
```
