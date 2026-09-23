# dvc-optuna — an Optuna search driven through a DVC pipeline

## What this is

A prototype of one idea: DVC owns the pipeline, Optuna owns the search, and
`src/tune.py` joins them by turning each trial into a `dvc exp run -S` call.
The ML problem — scikit-learn's digits set, a `HistGradientBoostingClassifier` —
is deliberately trivial. It is a harness for testing the integration, not a
model worth caring about.

| File | Role |
| --- | --- |
| `dvc.yaml` | The three pipeline stages |
| `params.yaml` | Stage inputs; DVC tracks these per-key |
| `search.yaml` | The Optuna search space |
| `src/tune.py` | The glue |
| `docs/` | Rationale and behaviour notes, all linked from `README.md` |

Keep `search.yaml` out of `params.yaml`, and never add it to a stage's `params:`
list. If DVC can see the search space as a stage input, widening a range
invalidates every cached trial.

## Writing

- Concise but clear, in replies and in docs. Cut padding, never substance.
- Prefer tables and short sections to narrative.
- Ask before acting when direction is ambiguous — one question at a time.

## Conventions

- Python managed with `uv`. Run things as `uv run <cmd>`, never bare `python`.
- `ruff` for both linting and formatting, 100-column lines.

