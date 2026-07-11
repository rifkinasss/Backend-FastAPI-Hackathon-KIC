"""Fuzzy configuration route.

Endpoint:
  GET /api/v1/config/fuzzy — Return fuzzy membership function configuration
"""

from fastapi import APIRouter

from app.fuzzy.config import konfigurasi_fuzzy
from app.fuzzy.membership import mf_data


router = APIRouter(prefix="/api/v1/config", tags=["Configuration"])


@router.get("/fuzzy")
def get_fuzzy_config():
    """Return fuzzy membership function configuration for all parameters.

    Used by the dashboard to render membership function charts.
    """
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
    return {"data": serialized_config}
