"""Score the trained model on the held-out test split."""

import joblib

from common import MODEL_PATH, load_split, score, write_metrics


def main() -> None:
    model = joblib.load(MODEL_PATH)
    write_metrics("test", score(model, *load_split("test")))


if __name__ == "__main__":
    main()
