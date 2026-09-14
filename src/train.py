"""Fit a gradient-boosted classifier and score it on the validation split."""

from pathlib import Path

import joblib
import yaml
from sklearn.ensemble import HistGradientBoostingClassifier

from common import MODEL_PATH, load_split, score, write_metrics


def build_model(params: dict) -> HistGradientBoostingClassifier:
    return HistGradientBoostingClassifier(
        max_iter=params["max_iter"],
        learning_rate=params["learning_rate"],
        max_depth=params["max_depth"],
        max_leaf_nodes=params["max_leaf_nodes"],
        min_samples_leaf=params["min_samples_leaf"],
        l2_regularization=params["l2_regularization"],
        random_state=params["seed"],
    )


def main() -> None:
    params = yaml.safe_load(Path("params.yaml").read_text())["train"]

    X_train, y_train = load_split("train")
    model = build_model(params).fit(X_train, y_train)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    write_metrics("valid", score(model, *load_split("valid")))


if __name__ == "__main__":
    main()
