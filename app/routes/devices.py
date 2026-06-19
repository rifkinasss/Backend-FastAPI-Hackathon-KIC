from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.services.device_command_service import (
    acknowledge_device_command,
    create_device_command,
    get_next_device_command,
    list_device_states,
)


router = APIRouter(prefix="/api/devices", tags=["Device Commands"])


class DeviceCommandRequest(BaseModel):
    command: str = Field(examples=["turn_off"])
    requested_by: Optional[str] = Field(default="dashboard", examples=["dashboard"])


class DeviceCommandAckRequest(BaseModel):
    status: str = Field(default="acknowledged", examples=["acknowledged"])
    error_message: Optional[str] = Field(default=None, examples=["Relay timeout"])


@router.get("/states")
def get_device_states():
    try:
        return list_device_states()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{device_id}/commands", status_code=201)
def post_device_command(device_id: str, payload: DeviceCommandRequest):
    try:
        command = create_device_command(
            device_id=device_id,
            command=payload.command,
            requested_by=payload.requested_by,
        )
        return {"message": "Command berhasil dibuat", "data": command}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{device_id}/commands/next")
def get_next_command(device_id: str):
    try:
        command = get_next_device_command(device_id)
        return {"data": command}
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{device_id}/commands/{command_id}/ack")
def post_command_ack(
    device_id: str,
    command_id: int,
    payload: DeviceCommandAckRequest,
):
    try:
        command = acknowledge_device_command(
            device_id=device_id,
            command_id=command_id,
            status=payload.status,
            error_message=payload.error_message,
        )
        return {"message": "Command acknowledgement berhasil disimpan", "data": command}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
