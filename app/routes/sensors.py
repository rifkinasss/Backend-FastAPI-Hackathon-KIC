from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app.core.postgresql import create_db_and_tables, get_postgres_engine
from app.models import DustReading, GasReading, HeavyEquipmentReading
from app.services.device_command_service import update_state_from_reading


router = APIRouter(prefix="/api/sensors", tags=["Sensor Readings"])


class SensorReadingRequest(BaseModel):
    device_id: str = Field(examples=["DB001"])
    type: Literal["debu", "gas", "emisi"] = Field(examples=["debu"])
    location: Optional[str] = Field(default=None, examples=["Jalan Tambang A"])
    recorded_at: Optional[datetime] = Field(default=None, examples=["2026-06-18T20:10:00Z"])
    pm25: Optional[float] = Field(default=None, examples=[35.0])
    pm10: Optional[float] = Field(default=None, examples=[82.0])
    ch4: Optional[float] = Field(default=None, examples=[0.4])
    h2s: Optional[float] = Field(default=None, examples=[2.0])
    co: Optional[float] = Field(default=None, examples=[12.0])
    co2: Optional[float] = Field(default=None, examples=[680.0])
    temperature: Optional[float] = Field(default=None, examples=[31.5])
    humidity: Optional[float] = Field(default=None, examples=[72.0])


@router.post("/readings", status_code=201)
def create_sensor_reading(payload: SensorReadingRequest):
    create_db_and_tables()

    try:
        row = build_reading_row(payload)
        with Session(get_postgres_engine()) as session:
            session.add(row)
            session.commit()
            session.refresh(row)

        state = update_state_from_reading(payload.device_id, payload.location)

        return {
            "message": "Data sensor berhasil disimpan",
            "data": {
                "id": row.id,
                "device_id": payload.device_id,
                "type": payload.type,
                "recorded_at": row.waktu.isoformat(),
            },
            "state": state,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def build_reading_row(payload: SensorReadingRequest):
    recorded_at = payload.recorded_at or datetime.now(timezone.utc)
    base_payload = {
        "waktu": recorded_at,
        "sensor_id": payload.device_id.strip(),
        "lokasi": payload.location,
        "suhu": to_decimal(payload.temperature),
        "kelembaban": to_decimal(payload.humidity),
    }

    if not base_payload["sensor_id"]:
        raise ValueError("device_id tidak boleh kosong")

    if payload.type == "debu":
        return DustReading(
            **base_payload,
            pm25=to_decimal(payload.pm25),
            pm10=to_decimal(payload.pm10),
        )

    if payload.type == "gas":
        return GasReading(
            **base_payload,
            ch4=to_decimal(payload.ch4),
            h2s=to_decimal(payload.h2s),
        )

    return HeavyEquipmentReading(
        **base_payload,
        co=to_decimal(payload.co),
        co2=to_decimal(payload.co2),
    )


def to_decimal(value: float | None):
    if value is None:
        return None

    return Decimal(str(value))
