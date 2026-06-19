from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from app.core.env import build_postgres_url, load_environment


load_environment()

DB_CONFIG = build_postgres_url()
DATASET_DIR = Path(__file__).resolve().parent / "dataset"

TABLES = {
    "debu_tambang.csv": "tb_debu_tambang",
    "gas_tambang.csv": "tb_gas_tambang",
    "emisi_alat_berat.csv": "tb_emisi_alat_berat",
}


def load_csv(path):
    df = pd.read_csv(path)
    df["waktu"] = pd.to_datetime(df["waktu"])
    df["sensor_id"] = df["sensor_id"].astype(str).str.strip()
    df["lokasi"] = df["lokasi"].astype(str).str.strip()
    return df


def main():
    engine = create_engine(DB_CONFIG)

    for filename, table_name in TABLES.items():
        path = DATASET_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        df = load_csv(path)
        with engine.begin() as connection:
            connection.execute(text(f"DELETE FROM {table_name}"))

        df.to_sql(table_name, engine, if_exists="append", index=False)
        print(f"Imported {len(df)} rows from {filename} into {table_name}")


if __name__ == "__main__":
    main()
