"""Device CRUD service.

Handles Create, Read, Update, Delete for devices table.
Also manages device_configs and device_states as sub-resources.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from app.core.postgresql import get_postgres_engine
from app.models import Device, DeviceCommand, DeviceConfig, DeviceSensor, SensorDefinition, DeviceState


# ── Helpers ──────────────────────────────────────────────────


def _get_session() -> Session:
    return Session(get_postgres_engine())


def _to_decimal(value: float | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _serialize_device(device: Device) -> dict[str, Any]:
    return {
        "id": str(device.id),
        "device_code": device.device_code,
        "hardware_id": device.hardware_id,
        "device_name": device.device_name,
        "location": device.location,
        "latitude": float(device.latitude) if device.latitude is not None else None,
        "longitude": float(device.longitude) if device.longitude is not None else None,
        "firmware_ver": device.firmware_ver,
        "description": device.description,
        "is_active": device.is_active,
        "provisioning_status": device.provisioning_status,
        "created_at": device.created_at.isoformat() if device.created_at else None,
        "updated_at": device.updated_at.isoformat() if device.updated_at else None,
    }


def _serialize_config(cfg: DeviceConfig) -> dict[str, Any]:
    return {
        "id": cfg.id,
        "device_id": str(cfg.device_id),
        "config_key": cfg.config_key,
        "config_value": cfg.config_value,
        "config_json": cfg.config_json,
        "description": cfg.description,
        "is_active": cfg.is_active,
        "created_at": cfg.created_at.isoformat() if cfg.created_at else None,
        "updated_at": cfg.updated_at.isoformat() if cfg.updated_at else None,
    }


def _serialize_state(state: DeviceState) -> dict[str, Any]:
    return {
        "id": state.id,
        "device_id": str(state.device_id),
        "is_online": state.is_online,
        "power_state": state.power_state,
        "battery_voltage": float(state.battery_voltage) if state.battery_voltage is not None else None,
        "wifi_rssi": state.wifi_rssi,
        "uptime_seconds": state.uptime_seconds,
        "last_seen_at": state.last_seen_at.isoformat() if state.last_seen_at else None,
        "last_boot_at": state.last_boot_at.isoformat() if state.last_boot_at else None,
        "last_command_at": state.last_command_at.isoformat() if state.last_command_at else None,
        "updated_at": state.updated_at.isoformat() if state.updated_at else None,
    }


def _resolve_device(session: Session, device_id: str) -> Device:
    """Look up device by UUID or device_code."""
    # Try UUID first
    try:
        uid = UUID(device_id)
        device = session.get(Device, uid)
        if device:
            return device
    except ValueError:
        pass

    # Fall back to device_code
    device = session.exec(
        select(Device).where(Device.device_code == device_id)
    ).first()

    if device is None:
        raise LookupError(f"Device '{device_id}' tidak ditemukan")
    return device


# ── Device CRUD ──────────────────────────────────────────────


def create_device(
    *,
    device_code: str,
    device_name: str,
    location: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    firmware_ver: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Register a new ESP32 device and initialise its state."""

    with _get_session() as session:
        # Check for duplicate code
        existing = session.exec(
            select(Device).where(Device.device_code == device_code)
        ).first()
        if existing:
            raise ValueError(f"Device code '{device_code}' sudah terdaftar")

        device = Device(
            device_code=device_code.strip(),
            device_name=device_name.strip(),
            location=location,
            latitude=_to_decimal(latitude),
            longitude=_to_decimal(longitude),
            firmware_ver=firmware_ver,
            description=description,
        )
        session.add(device)
        session.flush()

        # Auto-create initial state row (1:1)
        state = DeviceState(
            device_id=device.id,
            is_online=False,
            power_state="off",
        )
        session.add(state)

        session.commit()
        session.refresh(device)
        return _serialize_device(device)


def list_devices(*, include_inactive: bool = False) -> list[dict[str, Any]]:
    """List all registered devices."""

    with _get_session() as session:
        stmt = select(Device).order_by(Device.device_code)
        if not include_inactive:
            stmt = stmt.where(Device.is_active == True)  # noqa: E712

        rows = session.exec(stmt).all()
    return [_serialize_device(d) for d in rows]


def provision_device(*, hardware_id: str, firmware_ver: str | None, wifi_rssi: int | None, sensors: list[dict[str, str | None]]) -> dict[str, Any]:
    """Register a newly flashed ESP32 and map its reported sensors.

    New devices remain pending until an operator supplies their deployment location.
    Subsequent calls are heartbeats and only refresh firmware/state information.
    """
    with _get_session() as session:
        device = session.exec(select(Device).where(Device.hardware_id == hardware_id)).first()
        created = device is None
        if device is None:
            compact_id = hardware_id.replace(":", "").replace("-", "")[-12:].upper()
            device = Device(
                device_code=f"ESP32-{compact_id}",
                device_name=f"ESP32 {compact_id}",
                hardware_id=hardware_id,
                firmware_ver=firmware_ver,
                provisioning_status="pending",
            )
            session.add(device)
            session.flush()
            now = datetime.now(timezone.utc)
            session.add(DeviceState(
                device_id=device.id,
                is_online=True,
                power_state="on",
                last_seen_at=now,
                last_boot_at=now,
                wifi_rssi=wifi_rssi,
            ))
        elif firmware_ver:
            device.firmware_ver = firmware_ver

        now = datetime.now(timezone.utc)
        state = session.exec(select(DeviceState).where(DeviceState.device_id == device.id)).first()
        if state:
            state.is_online = True
            state.power_state = "on"
            state.last_seen_at = now
            state.last_boot_at = now
            state.wifi_rssi = wifi_rssi

        mapped = []
        for sensor in sensors:
            code = (sensor["sensor_code"] or "").strip().upper()
            if not code:
                continue
            definition = session.exec(select(SensorDefinition).where(SensorDefinition.sensor_code == code)).first()
            if definition is None:
                continue
            mapping = session.exec(
                select(DeviceSensor).where(
                    DeviceSensor.device_id == device.id,
                    DeviceSensor.sensor_def_id == definition.id,
                )
            ).first()
            if mapping is None:
                session.add(DeviceSensor(
                    device_id=device.id,
                    sensor_def_id=definition.id,
                    gpio_pin=sensor.get("gpio_pin"),
                    i2c_address=sensor.get("i2c_address"),
                    notes="Terdeteksi otomatis saat provisioning",
                ))
            mapped.append(code)

        session.add(device)
        session.commit()
        session.refresh(device)
        return {"created": created, "device": _serialize_device(device), "detected_sensors": mapped}


def set_provisioning_status(device_id: str, status: str) -> dict[str, Any]:
    with _get_session() as session:
        device = _resolve_device(session, device_id)
        device.provisioning_status = status
        session.add(device)
        session.commit()
        session.refresh(device)
        return _serialize_device(device)


def get_device(device_id: str) -> dict[str, Any]:
    """Get a single device by UUID or device_code."""

    with _get_session() as session:
        device = _resolve_device(session, device_id)
        return _serialize_device(device)


def update_device(
    device_id: str,
    *,
    device_name: str | None = None,
    location: str | None = None,
    latitude: float | None = ...,
    longitude: float | None = ...,
    firmware_ver: str | None = ...,
    description: str | None = ...,
    is_active: bool | None = None,
) -> dict[str, Any]:
    """Update device fields. Only provided fields are changed."""

    with _get_session() as session:
        device = _resolve_device(session, device_id)

        if device_name is not None:
            device.device_name = device_name.strip()
        if location is not None:
            device.location = location
        if latitude is not ...:
            device.latitude = _to_decimal(latitude)
        if longitude is not ...:
            device.longitude = _to_decimal(longitude)
        if firmware_ver is not ...:
            device.firmware_ver = firmware_ver
        if description is not ...:
            device.description = description
        if is_active is not None:
            device.is_active = is_active

        session.add(device)
        session.commit()
        session.refresh(device)
        return _serialize_device(device)


def delete_device(device_id: str, *, hard: bool = False) -> dict[str, Any]:
    """Soft-delete (default) or hard-delete a device.

    Soft-delete sets is_active = False.
    Hard-delete removes the row and cascades to all related data.
    """

    with _get_session() as session:
        device = _resolve_device(session, device_id)

        if hard:
            device_data = _serialize_device(device)
            session.delete(device)
            session.commit()
            return device_data

        device.is_active = False
        session.add(device)
        session.commit()
        session.refresh(device)
        return _serialize_device(device)


# ── Device State ─────────────────────────────────────────────


def get_device_state(device_id: str) -> dict[str, Any]:
    """Get the real-time state of a device."""

    with _get_session() as session:
        device = _resolve_device(session, device_id)
        state = session.exec(
            select(DeviceState).where(DeviceState.device_id == device.id)
        ).first()
        if state is None:
            raise LookupError(f"State untuk device '{device_id}' tidak ditemukan")
        return _serialize_state(state)


def list_device_states() -> list[dict[str, Any]]:
    """List all device states."""

    with _get_session() as session:
        states = session.exec(
            select(DeviceState, Device)
            .join(Device, DeviceState.device_id == Device.id)
            .order_by(Device.device_code)
        ).all()
        result = []
        for state, device in states:
            data = _serialize_state(state)
            data["device_code"] = device.device_code
            data["device_name"] = device.device_name
            result.append(data)
        return result


# ── Device Config ────────────────────────────────────────────


def get_device_configs(device_id: str) -> list[dict[str, Any]]:
    """List all configs for a device."""

    with _get_session() as session:
        device = _resolve_device(session, device_id)
        configs = session.exec(
            select(DeviceConfig)
            .where(DeviceConfig.device_id == device.id)
            .order_by(DeviceConfig.config_key)
        ).all()
        return [_serialize_config(c) for c in configs]


def set_device_config(
    device_id: str,
    *,
    config_key: str,
    config_value: str | None = None,
    config_json: dict | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create or update a device config (upsert by config_key)."""

    with _get_session() as session:
        device = _resolve_device(session, device_id)

        cfg = session.exec(
            select(DeviceConfig)
            .where(DeviceConfig.device_id == device.id)
            .where(DeviceConfig.config_key == config_key)
        ).first()

        if cfg is None:
            cfg = DeviceConfig(
                device_id=device.id,
                config_key=config_key.strip(),
                config_value=config_value,
                config_json=config_json,
                description=description,
            )
            session.add(cfg)
        else:
            if config_value is not None:
                cfg.config_value = config_value
            if config_json is not None:
                cfg.config_json = config_json
            if description is not None:
                cfg.description = description
            session.add(cfg)

        session.commit()
        session.refresh(cfg)
        return _serialize_config(cfg)


def delete_device_config(device_id: str, config_key: str) -> dict[str, Any]:
    """Delete a specific config entry for a device."""

    with _get_session() as session:
        device = _resolve_device(session, device_id)
        cfg = session.exec(
            select(DeviceConfig)
            .where(DeviceConfig.device_id == device.id)
            .where(DeviceConfig.config_key == config_key)
        ).first()
        if cfg is None:
            raise LookupError(f"Config '{config_key}' tidak ditemukan untuk device '{device_id}'")

        data = _serialize_config(cfg)
        session.delete(cfg)
        session.commit()
        return data


def create_device_command(
    device_id: str,
    *,
    command: str,
    requested_by: str | None = "dashboard",
) -> dict[str, Any]:
    """Queue a remote control command for a device and update its power state if needed."""
    with _get_session() as session:
        device = _resolve_device(session, device_id)

        # Create the command
        cmd = DeviceCommand(
            device_id=device.id,
            command=command,
            requested_by=requested_by,
            status="pending",
        )
        session.add(cmd)

        # Keep the previous state until the ESP32 confirms the command via /ack.
        state = session.exec(
            select(DeviceState).where(DeviceState.device_id == device.id)
        ).first()
        if state:
            state.last_command_at = datetime.now(timezone.utc)
            session.add(state)

        session.commit()
        session.refresh(cmd)

        # Return serialized command
        return {
            "id": cmd.id,
            "device_id": str(cmd.device_id),
            "command": cmd.command,
            "status": cmd.status,
            "requested_by": cmd.requested_by,
            "created_at": cmd.created_at.isoformat() if cmd.created_at else None,
        }


def get_next_device_command(device_id: str) -> dict[str, Any] | None:
    """Fetch the oldest pending command and treat the poll as a heartbeat."""
    with _get_session() as session:
        device = _resolve_device(session, device_id)

        state = session.exec(
            select(DeviceState).where(DeviceState.device_id == device.id)
        ).first()
        if state:
            state.is_online = True
            state.last_seen_at = datetime.now(timezone.utc)
            session.add(state)

        cmd = session.exec(
            select(DeviceCommand)
            .where(DeviceCommand.device_id == device.id)
            .where(DeviceCommand.status == "pending")
            .order_by(DeviceCommand.created_at)
        ).first()

        if cmd is None:
            session.commit()
            return None

        # Update status to 'sent'
        cmd.status = "sent"
        session.add(cmd)
        session.commit()
        session.refresh(cmd)

        return {
            "id": cmd.id,
            "device_id": str(cmd.device_id),
            "command": cmd.command,
            "status": cmd.status,
            "requested_by": cmd.requested_by,
            "created_at": cmd.created_at.isoformat() if cmd.created_at else None,
        }


def acknowledge_device_command(
    device_id: str,
    command_id: int,
    *,
    status: str,
    error_message: str | None = None,
) -> dict[str, Any]:
    """Acknowledge or fail a command that was sent to the device, updating the device state."""
    if status not in ("acknowledged", "failed", "executed"):
        raise ValueError("Status ack harus salah satu dari: acknowledged, failed, executed")

    with _get_session() as session:
        device = _resolve_device(session, device_id)

        cmd = session.exec(
            select(DeviceCommand)
            .where(DeviceCommand.id == command_id)
            .where(DeviceCommand.device_id == device.id)
        ).first()

        if cmd is None:
            raise LookupError(f"Command ID {command_id} tidak ditemukan untuk device '{device_id}'")

        cmd.status = status
        cmd.error_message = error_message
        cmd.acknowledged_at = datetime.now(timezone.utc)
        if status == "executed":
            cmd.executed_at = datetime.now(timezone.utc)
        session.add(cmd)

        # Update device state power status
        state = session.exec(
            select(DeviceState).where(DeviceState.device_id == device.id)
        ).first()
        if state:
            if status in ("acknowledged", "executed"):
                if cmd.command == "turn_off":
                    # "Off" means monitoring disabled. ESP32 stays online so it can
                    # receive a later turn_on command without a physical reset.
                    state.power_state = "off"
                    state.is_online = True
                elif cmd.command == "turn_on":
                    state.power_state = "on"
                    state.is_online = True
                elif cmd.command == "restart":
                    state.power_state = "on"
                    state.is_online = True
            elif status == "failed":
                state.power_state = "error"
            session.add(state)

        session.commit()
        session.refresh(cmd)

        return {
            "id": cmd.id,
            "device_id": str(cmd.device_id),
            "command": cmd.command,
            "status": cmd.status,
            "requested_by": cmd.requested_by,
            "error_message": cmd.error_message,
            "created_at": cmd.created_at.isoformat() if cmd.created_at else None,
            "acknowledged_at": cmd.acknowledged_at.isoformat() if cmd.acknowledged_at else None,
        }
