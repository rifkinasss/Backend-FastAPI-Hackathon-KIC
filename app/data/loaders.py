"""Data loaders for the fuzzy/analysis pipeline.

Reads from the new SIMOSI schema (sensor_readings + detail tables)
and returns DataFrames in the format expected by the fuzzy engine.

Output format per category (preserves column names used by fuzzy):
  DEBU TAMBANG:      waktu, device_code, pm25, pm10, suhu, kelembaban
  GAS TAMBANG:       waktu, device_code, ch4, h2s, suhu, kelembaban
  EMISI ALAT BERAT:  waktu, device_code, co, co2, suhu, kelembaban
"""

import pandas as pd
from sqlalchemy import text

from app.core.config import DATASET_DIR, DATASET_FILES, DATA_SOURCE, engine


# ── New schema queries ───────────────────────────────────────

_SQL_DEBU = text("""
    SELECT
        sr.recorded_at   AS waktu,
        d.device_code    AS device_code,
        d.location       AS lokasi,
        dd.pm25,
        dd.pm10,
        sr.temperature   AS suhu,
        sr.humidity      AS kelembaban
    FROM sensor_readings sr
    JOIN devices d            ON d.id = sr.device_id
    JOIN tb_debu_tambang dd   ON dd.reading_id = sr.id
    WHERE sr.recorded_at BETWEEN :start_time AND :end_time
    ORDER BY sr.recorded_at
""")

_SQL_GAS = text("""
    SELECT
        sr.recorded_at   AS waktu,
        d.device_code    AS device_code,
        d.location       AS lokasi,
        gg.ch4,
        gg.h2s,
        sr.temperature   AS suhu,
        sr.humidity      AS kelembaban
    FROM sensor_readings sr
    JOIN devices d           ON d.id = sr.device_id
    JOIN tb_gas_tambang gg   ON gg.reading_id = sr.id
    WHERE sr.recorded_at BETWEEN :start_time AND :end_time
    ORDER BY sr.recorded_at
""")

_SQL_EMISI = text("""
    SELECT
        sr.recorded_at     AS waktu,
        d.device_code      AS device_code,
        d.location         AS lokasi,
        ee.co,
        ee.co2_estimated   AS co2,
        sr.temperature     AS suhu,
        sr.humidity        AS kelembaban
    FROM sensor_readings sr
    JOIN devices d                  ON d.id = sr.device_id
    JOIN tb_emisi_alat_berat ee     ON ee.reading_id = sr.id
    WHERE sr.recorded_at BETWEEN :start_time AND :end_time
    ORDER BY sr.recorded_at
""")

_CATEGORY_QUERIES = {
    "DEBU TAMBANG": _SQL_DEBU,
    "GAS TAMBANG": _SQL_GAS,
    "EMISI ALAT BERAT": _SQL_EMISI,
}


# ── DataFrame cleaning ──────────────────────────────────────


def clean_sensor_frame(df):
    df = df.copy()
    if df.empty:
        return df

    df["waktu"] = pd.to_datetime(df["waktu"])

    # Backwards compat: analysis_service uses "sensor_id" for grouping.
    # Map device_code → sensor_id so fuzzy engine keeps working.
    if "device_code" in df.columns:
        df["sensor_id"] = df["device_code"].astype(str).str.strip()
    elif "sensor_id" in df.columns:
        df["sensor_id"] = df["sensor_id"].astype(str).str.strip()

    if "lokasi" in df.columns:
        df["lokasi"] = df["lokasi"].astype(str).str.strip()

    return df


# ── CSV loaders (fallback / legacy) ─────────────────────────


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


def read_full_csv_dataset(dataset_name):
    filename = DATASET_FILES[dataset_name]
    return clean_sensor_frame(pd.read_csv(DATASET_DIR / filename))


def latest_timestamp_from_csv():
    df = pd.read_csv(DATASET_DIR / "debu_tambang.csv", usecols=["waktu"])
    df["waktu"] = pd.to_datetime(df["waktu"])
    if df.empty:
        return None
    return df["waktu"].max()


# ── Database loaders (new schema) ────────────────────────────


def read_sql_category(category, fetch_start, fetch_end):
    """Read a category from the new schema using JOINed queries."""
    query = _CATEGORY_QUERIES[category]
    df = pd.read_sql(query, engine, params={"start_time": fetch_start, "end_time": fetch_end})
    return clean_sensor_frame(df)


def load_from_database(fetch_start, fetch_end):
    return {
        category: read_sql_category(category, fetch_start, fetch_end)
        for category in _CATEGORY_QUERIES
    }


def load_datasets(fetch_start, fetch_end):
    if DATA_SOURCE == "csv":
        return load_from_csv(fetch_start, fetch_end)

    try:
        return load_from_database(fetch_start, fetch_end)
    except Exception as exc:
        print(f"PostgreSQL unavailable, loading CSV datasets instead: {exc}")
        return load_from_csv(fetch_start, fetch_end)


def latest_timestamp():
    if DATA_SOURCE == "csv":
        return latest_timestamp_from_csv()

    try:
        result = pd.read_sql(
            text("SELECT recorded_at AS waktu FROM sensor_readings ORDER BY recorded_at DESC LIMIT 1"),
            engine,
        )
        if not result.empty:
            return pd.to_datetime(result["waktu"].iloc[0])
    except Exception as exc:
        print(f"PostgreSQL latest timestamp unavailable, checking CSV datasets instead: {exc}")

    return latest_timestamp_from_csv()
