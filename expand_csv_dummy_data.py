import argparse
import shutil
from pathlib import Path

import numpy as np
import pandas as pd


DATASET_DIR = Path(__file__).resolve().parents[2] / "iot-fuzzy-kideco" / "dataset"
DATASET_FILES = [
    "debu_tambang.csv",
    "gas_tambang.csv",
    "emisi_alat_berat.csv",
]
TEXT_COLUMNS = {"sensor_id", "lokasi"}
TIME_COLUMN = "waktu"


def parse_args():
    parser = argparse.ArgumentParser(description="Expand IoT fuzzy CSV datasets with dummy rows.")
    parser.add_argument("--target-rows", type=int, default=500, help="Total rows per CSV file.")
    parser.add_argument("--jitter", type=float, default=0.04, help="Numeric variation ratio.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create .original.csv backups before overwriting CSV files.",
    )
    return parser.parse_args()


def numeric_columns(df):
    return [
        column
        for column in df.columns
        if column not in {TIME_COLUMN, *TEXT_COLUMNS}
    ]


def infer_interval(df):
    deltas = df[TIME_COLUMN].sort_values().diff().dropna()
    if deltas.empty:
        return pd.Timedelta(minutes=5)

    interval = deltas.median()
    if pd.isna(interval) or interval <= pd.Timedelta(0):
        return pd.Timedelta(minutes=5)

    return interval


def clean_number(value):
    rounded = round(float(value), 3)
    if rounded.is_integer():
        return int(rounded)
    return rounded


def expand_file(path, target_rows, jitter, rng, create_backup):
    df = pd.read_csv(path)
    df[TIME_COLUMN] = pd.to_datetime(df[TIME_COLUMN])
    df = df.sort_values(TIME_COLUMN).reset_index(drop=True)

    if target_rows <= len(df):
        print(f"{path.name}: already has {len(df)} rows, skipped")
        return

    if create_backup:
        backup_path = path.with_suffix(".original.csv")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)

    interval = infer_interval(df)
    nums = numeric_columns(df)
    rows = df.to_dict("records")
    last_time = df[TIME_COLUMN].max()

    while len(rows) < target_rows:
        source = rows[(len(rows) - len(df)) % len(df)].copy()
        last_time = last_time + interval
        source[TIME_COLUMN] = last_time

        for column in nums:
            value = float(source[column])
            if jitter > 0:
                scale = max(abs(value) * jitter, jitter)
                value = max(0.0, value + rng.normal(0, scale))
            source[column] = clean_number(value)

        rows.append(source)

    expanded = pd.DataFrame(rows[:target_rows], columns=df.columns)
    expanded[TIME_COLUMN] = pd.to_datetime(expanded[TIME_COLUMN]).dt.strftime("%Y-%m-%d %H:%M:%S")
    expanded.to_csv(path, index=False)
    print(f"{path.name}: {len(df)} -> {len(expanded)} rows")


def main():
    args = parse_args()
    rng = np.random.default_rng(args.seed)

    for filename in DATASET_FILES:
        expand_file(
            DATASET_DIR / filename,
            target_rows=args.target_rows,
            jitter=args.jitter,
            rng=rng,
            create_backup=not args.no_backup,
        )


if __name__ == "__main__":
    main()
