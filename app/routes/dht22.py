from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.services.dht22_service import store_dht22_reading


router = APIRouter(prefix="/api/sensors/dht22", tags=["DHT22 Sensor"])


class DHT22ReadingRequest(BaseModel):
    device_id: Optional[str] = Field(default="DHT22-001", examples=["DHT22-001"])
    device_name: Optional[str] = Field(default=None, examples=["DHT 22 Greenhouse 1"])
    location: Optional[str] = Field(default=None, examples=["Greenhouse A"])
    description: Optional[str] = Field(default=None, examples=["Sensor suhu dan kelembaban area greenhouse"])
    temperature: float = Field(examples=[29.4])
    humidity: float = Field(examples=[72.8])
    recorded_at: Optional[datetime] = Field(default=None, examples=["2026-06-17T08:00:00Z"])


@router.post("/readings", status_code=201)
def create_dht22_reading(payload: DHT22ReadingRequest):
    try:
        reading = store_dht22_reading(payload.model_dump(mode="json", exclude_none=True))
        return {"message": "Data DHT22 berhasil disimpan", "data": reading}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Gagal menyimpan data ke database",
                "error": str(exc),
            },
        ) from exc
