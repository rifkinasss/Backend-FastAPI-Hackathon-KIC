from fastapi import APIRouter

from app.fuzzy.config import konfigurasi_fuzzy
from app.fuzzy.membership import mf_data


router = APIRouter()


@router.get("/config")
def get_config():
    serialized_config = {}
    for var, cfg in konfigurasi_fuzzy.items():
        mf = mf_data[var]
        serialized_config[var] = {
            "nama": cfg["nama"],
            "rentang": cfg["rentang"],
            "batas_titik": cfg["batas_titik"],
            "mf": {
                "x": mf["x"].tolist(),
                "lo": mf["lo"].tolist(),
                "md": mf["md"].tolist(),
                "hi": mf["hi"].tolist(),
            },
        }
    return serialized_config

