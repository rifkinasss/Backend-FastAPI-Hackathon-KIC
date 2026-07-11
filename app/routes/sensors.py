"""Sensor definitions and device-sensor mapping routes.

Endpoints:
  POST   /api/v1/sensors/definitions        — Create sensor type
  GET    /api/v1/sensors/definitions        — List sensor types
  DELETE /api/v1/sensors/definitions/{id}   — Delete sensor type

  POST   /api/v1/devices/{id}/sensors       — Install sensor on device
  GET    /api/v1/devices/{id}/sensors       — List sensors on device
  DELETE /api/v1/devices/sensors/{mapping_id} — Uninstall sensor from device
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.services.sensor_service import (
    create_sensor_definition,
    delete_sensor_definition,
    list_device_sensors,
    list_sensor_definitions,
    map_sensor_to_device,
    unmap_sensor_from_device,
)


router = APIRouter(tags=["Sensors"])


# ── Pydantic Schemas ─────────────────────────────────────────


class SensorDefinitionCreate(BaseModel):
    sensor_code: str = Field(
        ..., min_length=1, max_length=50,
        examples=["DS3231"],
        description="Unique code identifying the sensor type.",
    )
    sensor_name: str = Field(
        ..., min_length=1, max_length=150,
        examples=["DS3231 Real-Time Clock"],
    )
    manufacturer: Optional[str] = Field(default=None, max_length=100, examples=["Maxim Integrated"])
    description: Optional[str] = Field(default=None)
    interface_type: Optional[str] = Field(
        default=None, max_length=30,
        examples=["i2c"],
        description="analog, digital, i2c, spi, uart, or onewire",
    )


class DeviceSensorMapRequest(BaseModel):
    sensor_def_id: int = Field(..., description="ID of the sensor definition from the catalog.")
    gpio_pin: Optional[str] = Field(default=None, max_length=20, examples=["GPIO4"])
    i2c_address: Optional[str] = Field(default=None, max_length=10, examples=["0x68"])
    install_date: Optional[date] = Field(default=None)
    notes: Optional[str] = Field(default=None)


# ── Sensor Definition routes ──────────────────────────────────


@router.post("/api/v1/sensors/definitions", status_code=201)
def api_create_sensor_definition(payload: SensorDefinitionCreate):
    """Add a new sensor type to the catalog."""
    try:
        sd = create_sensor_definition(
            sensor_code=payload.sensor_code,
            sensor_name=payload.sensor_name,
            manufacturer=payload.manufacturer,
            description=payload.description,
            interface_type=payload.interface_type,
        )
        return {"message": "Sensor definition berhasil dibuat", "data": sd}
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/sensors/definitions")
def api_list_sensor_definitions(include_inactive: bool = Query(False)):
    """List all supported sensor types in the catalog."""
    try:
        sds = list_sensor_definitions(include_inactive=include_inactive)
        return {"data": sds, "count": len(sds)}
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/api/v1/sensors/definitions/{sensor_def_id}")
def api_delete_sensor_definition(sensor_def_id: int):
    """Delete a sensor type from the catalog."""
    try:
        sd = delete_sensor_definition(sensor_def_id)
        return {"message": "Sensor definition berhasil dihapus", "data": sd}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ── Device-Sensor Mapping routes ──────────────────────────────


@router.post("/api/v1/devices/{device_id}/sensors", status_code=201)
def api_map_sensor(device_id: str, payload: DeviceSensorMapRequest):
    """Install/link a sensor catalog type to a physical device."""
    try:
        mapping = map_sensor_to_device(
            device_id=device_id,
            sensor_def_id=payload.sensor_def_id,
            gpio_pin=payload.gpio_pin,
            i2c_address=payload.i2c_address,
            install_date=payload.install_date,
            notes=payload.notes,
        )
        return {"message": "Sensor berhasil dikaitkan ke device", "data": mapping}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/devices/{device_id}/sensors")
def api_list_device_sensors(device_id: str):
    """List all sensors currently installed on a device."""
    try:
        mappings = list_device_sensors(device_id)
        return {"data": mappings, "count": len(mappings)}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/api/v1/devices/sensors/{mapping_id}")
def api_unmap_sensor(mapping_id: int):
    """Uninstall/unlink a sensor from a device."""
    try:
        mapping = unmap_sensor_from_device(mapping_id)
        return {"message": "Sensor berhasil dicopot dari device", "data": mapping}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
