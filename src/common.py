"""Small helpers shared by the pipeline stages."""

import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, log_loss

DATA_DIR = Path("data")
METRICS_DIR = Path("metrics")
MODEL_PATH = Path("model/model.joblib")


def load_split(name: str) -> tuple[pd.DataFrame, pd.Series]:
    frame = pd.read_csv(DATA_DIR / f"{name}.csv")
    return frame.drop(columns="target"), frame["target"]


def score(model, X, y) -> dict[str, float]:
    proba = model.predict_proba(X)
    pred = model.classes_[proba.argmax(axis=1)]
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "f1_macro": float(f1_score(y, pred, average="macro")),
        "logloss": float(log_loss(y, proba, labels=model.classes_)),
    }


def write_metrics(name: str, metrics: dict[str, float]) -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    path = METRICS_DIR / f"{name}.json"
    path.write_text(json.dumps(metrics, indent=2) + "\n")
    print(f"{path}: {metrics}")
