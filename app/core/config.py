import os
from pathlib import Path

from sqlalchemy import create_engine

from app.core.env import build_postgres_url, load_environment


load_environment()

DB_CONFIG = build_postgres_url()
DATA_SOURCE = os.getenv("IOT_FUZZY_DATA_SOURCE", "postgresql").lower()
DATASET_DIR = Path(__file__).resolve().parents[4] / "iot-fuzzy-kideco" / "dataset"

engine = create_engine(DB_CONFIG, pool_pre_ping=True)

DATASET_FILES = {
    "debu_tambang": "debu_tambang.csv",
    "gas_tambang": "gas_tambang.csv",
    "emisi_alat_berat": "emisi_alat_berat.csv",
}

DATABASE_TABLES = {
    "DEBU TAMBANG": "tb_debu_tambang",
    "GAS TAMBANG": "tb_gas_tambang",
    "EMISI ALAT BERAT": "tb_emisi_alat_berat",
}
