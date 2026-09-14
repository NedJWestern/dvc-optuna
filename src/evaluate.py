"""Score the trained model on the held-out test split."""

import sys
from pathlib import Path

import joblib

sys.path.insert(0, str(Path(__file__).parent))
from common import MODEL_PATH, load_split, score, write_metrics  # noqa: E402


def main() -> None:
    model = joblib.load(MODEL_PATH)
    write_metrics("test", score(model, *load_split("test")))


if __name__ == "__main__":
    main()
