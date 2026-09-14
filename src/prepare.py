"""Load the UCI handwritten-digits dataset and split it into train/valid/test CSVs."""

from pathlib import Path

import yaml
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

OUT_DIR = Path("data")


def main() -> None:
    params = yaml.safe_load(Path("params.yaml").read_text())["prepare"]
    seed = params["seed"]

    frame = load_digits(as_frame=True).frame

    train, test = train_test_split(
        frame,
        test_size=params["test_size"],
        random_state=seed,
        stratify=frame["target"],
    )
    # valid_size is a fraction of the whole dataset, not of what is left.
    valid_fraction = params["valid_size"] / (1.0 - params["test_size"])
    train, valid = train_test_split(
        train,
        test_size=valid_fraction,
        random_state=seed,
        stratify=train["target"],
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, split in (("train", train), ("valid", valid), ("test", test)):
        split.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: {len(split)} rows")


if __name__ == "__main__":
    main()
