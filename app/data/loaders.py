import pandas as pd
from sqlalchemy import text

from app.core.config import (
    DATABASE_TABLES,
    DATASET_DIR,
    DATASET_FILES,
    DATA_SOURCE,
    engine,
)


def clean_sensor_frame(df):
    df = df.copy()
    if df.empty:
        return df

    df["waktu"] = pd.to_datetime(df["waktu"])
    if "sensor_id" in df.columns:
        df["sensor_id"] = df["sensor_id"].astype(str).str.strip()
    if "lokasi" in df.columns:
        df["lokasi"] = df["lokasi"].astype(str).str.strip()

    return df


def read_csv_dataset(filename, fetch_start, fetch_end):
    path = DATASET_DIR / filename
    df = clean_sensor_frame(pd.read_csv(path))
    mask = (df["waktu"] >= pd.to_datetime(fetch_start)) & (df["waktu"] <= pd.to_datetime(fetch_end))
    return df.loc[mask].copy()


def load_from_csv(fetch_start, fetch_end):
    return {
        "DEBU TAMBANG": read_csv_dataset("debu_tambang.csv", fetch_start, fetch_end),
        "GAS TAMBANG": read_csv_dataset("gas_tambang.csv", fetch_start, fetch_end),
        "EMISI ALAT BERAT": read_csv_dataset("emisi_alat_berat.csv", fetch_start, fetch_end),
    }


def read_sql_table(table_name, fetch_start, fetch_end):
    query = text(f"SELECT * FROM {table_name} WHERE waktu BETWEEN :start_time AND :end_time")
    df = pd.read_sql(query, engine, params={"start_time": fetch_start, "end_time": fetch_end})
    return clean_sensor_frame(df)


def load_from_database(fetch_start, fetch_end):
    return {
        dataset_name: read_sql_table(table_name, fetch_start, fetch_end)
        for dataset_name, table_name in DATABASE_TABLES.items()
    }


def load_datasets(fetch_start, fetch_end):
    if DATA_SOURCE == "csv":
        return load_from_csv(fetch_start, fetch_end)

    try:
        return load_from_database(fetch_start, fetch_end)
    except Exception as exc:
        print(f"PostgreSQL unavailable, loading CSV datasets instead: {exc}")
        return load_from_csv(fetch_start, fetch_end)


def read_full_csv_dataset(dataset_name):
    filename = DATASET_FILES[dataset_name]
    return clean_sensor_frame(pd.read_csv(DATASET_DIR / filename))


def latest_timestamp_from_csv():
    # Match the database behavior: tb_debu_tambang is the realtime clock reference.
    df = pd.read_csv(DATASET_DIR / "debu_tambang.csv", usecols=["waktu"])
    df["waktu"] = pd.to_datetime(df["waktu"])
    if df.empty:
        return None

    return df["waktu"].max()


def latest_timestamp():
    if DATA_SOURCE == "csv":
        return latest_timestamp_from_csv()

    try:
        latest_ref = pd.read_sql(
            text(f"SELECT waktu FROM {DATABASE_TABLES['DEBU TAMBANG']} ORDER BY waktu DESC LIMIT 1"),
            engine,
        )
        if not latest_ref.empty:
            return pd.to_datetime(latest_ref["waktu"].iloc[0])
    except Exception as exc:
        print(f"PostgreSQL latest timestamp unavailable, checking CSV datasets instead: {exc}")

    return latest_timestamp_from_csv()

