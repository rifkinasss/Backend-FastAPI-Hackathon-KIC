"""Device management routes.

Endpoints:
  POST   /api/v1/devices                           — Register new device
  GET    /api/v1/devices                            — List all devices
  GET    /api/v1/devices/{device_id}                — Get device detail
  PUT    /api/v1/devices/{device_id}                — Update device
  DELETE /api/v1/devices/{device_id}                — Soft-delete device

  GET    /api/v1/devices/states                     — List all device states
  GET    /api/v1/devices/{device_id}/state          — Get device state

  GET    /api/v1/devices/{device_id}/configs        — List device configs
  PUT    /api/v1/devices/{device_id}/configs        — Set (upsert) config
  DELETE /api/v1/devices/{device_id}/configs/{key}  — Delete config
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.services.device_service import (
    acknowledge_device_command,
    create_device,
    create_device_command,
    delete_device,
    delete_device_config,
    get_device,
    get_device_configs,
    get_device_state,
    get_next_device_command,
    list_device_states,
    list_devices,
    set_device_config,
    update_device,
)



router = APIRouter(prefix="/api/v1/devices", tags=["Devices"])


# ── Pydantic Schemas ─────────────────────────────────────────


class DeviceCreateRequest(BaseModel):
    device_code: str = Field(
        ..., min_length=1, max_length=50,
        examples=["ESP32-MINE-002"],
        description="Unique human-readable device code.",
    )
    device_name: str = Field(
        ..., min_length=1, max_length=150,
        examples=["SIMOSI Node Beta"],
        description="Descriptive name for dashboard display.",
    )
    location: Optional[str] = Field(
        default=None, max_length=200,
        examples=["Area Tambang Utama - Pit 2"],
    )
    latitude: Optional[float] = Field(default=None, examples=[-1.8612000])
    longitude: Optional[float] = Field(default=None, examples=[116.2234000])
    firmware_ver: Optional[str] = Field(default=None, max_length=50, examples=["1.0.0"])
    description: Optional[str] = Field(
        default=None,
        examples=["Secondary monitoring node at Pit 2."],
    )


class DeviceUpdateRequest(BaseModel):
    device_name: Optional[str] = Field(default=None, max_length=150, examples=["SIMOSI Node Beta v2"])
    location: Optional[str] = Field(default=None, max_length=200)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    firmware_ver: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class DeviceConfigRequest(BaseModel):
    config_key: str = Field(
        ..., min_length=1, max_length=100,
        examples=["reading_interval_s"],
    )
    config_value: Optional[str] = Field(default=None, examples=["30"])
    config_json: Optional[dict] = Field(default=None)
    description: Optional[str] = Field(
        default=None,
        examples=["Sensor reading interval in seconds."],
    )


# ── Device CRUD ──────────────────────────────────────────────


@router.post("", status_code=201)
def api_create_device(payload: DeviceCreateRequest):
    """Register a new ESP32 device."""
    try:
        device = create_device(
            device_code=payload.device_code,
            device_name=payload.device_name,
            location=payload.location,
            latitude=payload.latitude,
            longitude=payload.longitude,
            firmware_ver=payload.firmware_ver,
            description=payload.description,
        )
        return {"message": "Device berhasil didaftarkan", "data": device}
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("")
def api_list_devices(include_inactive: bool = Query(False, description="Include deactivated devices")):
    """List all registered devices."""
    try:
        devices = list_devices(include_inactive=include_inactive)
        return {"data": devices, "count": len(devices)}
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/states")
def api_list_device_states():
    """List real-time state of all devices."""
    try:
        states = list_device_states()
        return {"data": states, "count": len(states)}
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{device_id}")
def api_get_device(device_id: str):
    """Get device detail by UUID or device_code."""
    try:
        device = get_device(device_id)
        return {"data": device}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{device_id}")
def api_update_device(device_id: str, payload: DeviceUpdateRequest):
    """Update device information. Only provided fields are changed."""
    try:
        # Build kwargs, using sentinel ... for nullable fields to distinguish
        # "not provided" from "explicitly set to None"
        kwargs = {}
        if payload.device_name is not None:
            kwargs["device_name"] = payload.device_name
        if payload.location is not None:
            kwargs["location"] = payload.location
        if payload.latitude is not None:
            kwargs["latitude"] = payload.latitude
        if payload.longitude is not None:
            kwargs["longitude"] = payload.longitude
        if payload.firmware_ver is not None:
            kwargs["firmware_ver"] = payload.firmware_ver
        if payload.description is not None:
            kwargs["description"] = payload.description
        if payload.is_active is not None:
            kwargs["is_active"] = payload.is_active

        if not kwargs:
            raise ValueError("Tidak ada field yang diupdate")

        device = update_device(device_id, **kwargs)
        return {"message": "Device berhasil diupdate", "data": device}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{device_id}")
def api_delete_device(device_id: str, hard: bool = Query(False, description="Hard delete (permanent)")):
    """Soft-delete a device (default). Use ?hard=true for permanent deletion."""
    try:
        device = delete_device(device_id, hard=hard)
        action = "dihapus permanen" if hard else "dinonaktifkan"
        return {"message": f"Device berhasil {action}", "data": device}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ── Device State ─────────────────────────────────────────────


@router.get("/{device_id}/state")
def api_get_device_state(device_id: str):
    """Get real-time operational state of a device."""
    try:
        state = get_device_state(device_id)
        return {"data": state}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ── Device Config ────────────────────────────────────────────


@router.get("/{device_id}/configs")
def api_get_device_configs(device_id: str):
    """List all configuration entries for a device."""
    try:
        configs = get_device_configs(device_id)
        return {"data": configs, "count": len(configs)}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{device_id}/configs")
def api_set_device_config(device_id: str, payload: DeviceConfigRequest):
    """Create or update a configuration entry (upsert by config_key)."""
    try:
        config = set_device_config(
            device_id,
            config_key=payload.config_key,
            config_value=payload.config_value,
            config_json=payload.config_json,
            description=payload.description,
        )
        return {"message": "Config berhasil disimpan", "data": config}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{device_id}/configs/{config_key}")
def api_delete_device_config(device_id: str, config_key: str):
    """Delete a specific configuration entry."""
    try:
        config = delete_device_config(device_id, config_key)
        return {"message": "Config berhasil dihapus", "data": config}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class DeviceCommandRequest(BaseModel):
    command: str = Field(
        ...,
        examples=["turn_on"],
        description="Command verb (e.g. turn_on, turn_off, restart).",
    )
    requested_by: Optional[str] = Field(default="dashboard")


@router.post("/{device_id}/commands", status_code=201)
def api_send_device_command(device_id: str, payload: DeviceCommandRequest):
    """Queue a remote control command for a device."""
    try:
        command = create_device_command(
            device_id,
            command=payload.command,
            requested_by=payload.requested_by,
        )
        return {"message": "Command berhasil dikirim", "data": command}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class DeviceCommandAckRequest(BaseModel):
    status: str = Field(
        ...,
        examples=["acknowledged"],
        description="Command status outcome (acknowledged, failed, executed).",
    )
    error_message: Optional[str] = Field(default=None, examples=["Sensor read timeout"])


@router.get("/{device_id}/commands/next")
def api_get_next_command(device_id: str):
    """Poll the next pending command for the ESP32 to execute."""
    try:
        command = get_next_device_command(device_id)
        return {"data": command}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{device_id}/commands/{command_id}/ack")
def api_ack_command(
    device_id: str,
    command_id: int,
    payload: DeviceCommandAckRequest,
):
    """Device reports execution status of a command back to backend."""
    try:
        command = acknowledge_device_command(
            device_id,
            command_id,
            status=payload.status,
            error_message=payload.error_message,
        )
        return {"message": "Command status updated successfully", "data": command}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

