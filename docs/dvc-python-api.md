# Why the DVC Python API

[← README](../README.md)

Each trial calls `Repo.reproduce()` in-process. The first version of `tune.py`
instead ran `dvc exp run -S` per trial, recording each trial as a named DVC
experiment. That was dropped: the experiment bookkeeping cost time and caused
problems that the study never needed solved.

## Problems with `dvc exp run` per trial

| Problem | Cause |
| --- | --- |
| Per-trial overhead | ~1.4s of experiment bookkeeping per trial, large next to stages this fast |
| Name collisions | Experiment names are scoped to the baseline commit, so a second study reused the first study's names |
| Ref sprawl | Every trial left a git ref under `.git/refs/exps/` |
| Results disappearing | Experiments are listed under their baseline commit, so after the next commit plain `dvc exp show` no longer lists them (`--all-commits` still does) |

## What `Repo.reproduce()` does instead

- Runs only the stages whose inputs changed, like `dvc repro`.
- Runs no `git` commands. Checked by putting a stub `git` binary on `PATH`.
- Opens the repo once for the whole study, not once per trial.
- Raises `ReproductionError` on a failed stage, which Optuna catches and records as a failed trial.

## What was given up, and why that is acceptable

| Lost | Replacement |
| --- | --- |
| A DVC experiment per trial | Optuna's storage is the record of the study |
| `dvc exp apply <trial>` | `tune.py` prints the `dvc exp run -S ...` command for the best trial |
| Per-trial outputs | Still kept, in DVC's run cache. See [Cache](cache.md) |

Keeping DVC's defaults beat adding workarounds to make experiments behave.
Any trial can be re-run as an experiment later.
