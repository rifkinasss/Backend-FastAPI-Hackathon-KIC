"""Device locations route.

Endpoint:
  GET /api/v1/locations — Return GPS locations of all active devices
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select

from app.core.postgresql import get_postgres_engine
from app.models import Device


router = APIRouter(prefix="/api/v1", tags=["Locations"])


@router.get("/locations")
def get_locations():
    """Return GPS coordinates of all active devices for map display."""
    try:
        with Session(get_postgres_engine()) as session:
            devices = session.exec(
                select(Device)
                .where(Device.is_active == True)  # noqa: E712
                .where(Device.latitude.isnot(None))
                .where(Device.longitude.isnot(None))
                .order_by(Device.device_code)
            ).all()

            return {
                "data": [
                    {
                        "id": str(device.id),
                        "device_code": device.device_code,
                        "name": device.device_name,
                        "location": device.location,
                        "lat": float(device.latitude),
                        "lng": float(device.longitude),
                    }
                    for device in devices
                ]
            }
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
