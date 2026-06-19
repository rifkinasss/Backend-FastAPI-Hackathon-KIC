from fastapi import APIRouter


router = APIRouter()


@router.get("/locations")
def get_locations():
    # Dummy stage: this shape is ready to be replaced by rows from sensors table.
    return [
        {"id": "DB001", "name": "Jalan Tambang A", "type": "Debu", "lat": -1.8542, "lng": 116.2156},
        {"id": "GS001", "name": "Area Dasar Tambang", "type": "Gas", "lat": -1.8612, "lng": 116.2234},
        {"id": "EM001", "name": "Bengkel Alat Berat", "type": "Emisi", "lat": -1.8485, "lng": 116.2089},
    ]

