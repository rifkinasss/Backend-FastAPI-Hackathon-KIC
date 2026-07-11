"""Sensor catalog and mapping services.

Handles:
- CRUD for Sensor Definitions
- Mapping/Unmapping of Sensors to Devices
"""

from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from app.core.postgresql import get_postgres_engine
from app.models import Device, DeviceSensor, SensorDefinition


def _get_session() -> Session:
    return Session(get_postgres_engine())


def _serialize_definition(sd: SensorDefinition) -> dict[str, Any]:
    return {
        "id": sd.id,
        "sensor_code": sd.sensor_code,
        "sensor_name": sd.sensor_name,
        "manufacturer": sd.manufacturer,
        "description": sd.description,
        "interface_type": sd.interface_type,
        "is_active": sd.is_active,
        "created_at": sd.created_at.isoformat() if sd.created_at else None,
        "updated_at": sd.updated_at.isoformat() if sd.updated_at else None,
    }


def _serialize_mapping(ds: DeviceSensor, sd: SensorDefinition) -> dict[str, Any]:
    return {
        "id": ds.id,
        "device_id": str(ds.device_id),
        "sensor_def_id": ds.sensor_def_id,
        "sensor_code": sd.sensor_code,
        "sensor_name": sd.sensor_name,
        "gpio_pin": ds.gpio_pin,
        "i2c_address": ds.i2c_address,
        "install_date": ds.install_date.isoformat() if ds.install_date else None,
        "is_active": ds.is_active,
        "notes": ds.notes,
        "created_at": ds.created_at.isoformat() if ds.created_at else None,
        "updated_at": ds.updated_at.isoformat() if ds.updated_at else None,
    }


# ── Sensor Definition CRUD ────────────────────────────────────


def create_sensor_definition(
    *,
    sensor_code: str,
    sensor_name: str,
    manufacturer: str | None = None,
    description: str | None = None,
    interface_type: str | None = None,
) -> dict[str, Any]:
    """Create a new sensor type in the master catalog."""
    with _get_session() as session:
        # Check duplicate
        existing = session.exec(
            select(SensorDefinition).where(SensorDefinition.sensor_code == sensor_code)
        ).first()
        if existing:
            raise ValueError(f"Sensor code '{sensor_code}' sudah terdaftar di katalog")

        sd = SensorDefinition(
            sensor_code=sensor_code.strip().upper(),
            sensor_name=sensor_name.strip(),
            manufacturer=manufacturer,
            description=description,
            interface_type=interface_type.strip().lower() if interface_type else None,
        )
        session.add(sd)
        session.commit()
        session.refresh(sd)
        return _serialize_definition(sd)


def list_sensor_definitions(*, include_inactive: bool = False) -> list[dict[str, Any]]:
    """List all sensor definitions in the catalog."""
    with _get_session() as session:
        stmt = select(SensorDefinition).order_by(SensorDefinition.sensor_code)
        if not include_inactive:
            stmt = stmt.where(SensorDefinition.is_active == True)  # noqa: E712

        rows = session.exec(stmt).all()
        return [_serialize_definition(sd) for sd in rows]


def delete_sensor_definition(sensor_def_id: int) -> dict[str, Any]:
    """Delete a sensor definition from the catalog (cascades to mappings)."""
    with _get_session() as session:
        sd = session.get(SensorDefinition, sensor_def_id)
        if sd is None:
            raise LookupError(f"Sensor Definition ID {sensor_def_id} tidak ditemukan")

        data = _serialize_definition(sd)
        session.delete(sd)
        session.commit()
        return data


# ── Device-Sensor Mapping ─────────────────────────────────────


def map_sensor_to_device(
    *,
    device_id: str,
    sensor_def_id: int,
    gpio_pin: str | None = None,
    i2c_address: str | None = None,
    install_date: date | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    """Map/install a sensor catalog item onto a physical device."""
    with _get_session() as session:
        # Resolve device (supports code or UUID)
        try:
            uid = UUID(device_id)
            device = session.get(Device, uid)
        except ValueError:
            device = session.exec(
                select(Device).where(Device.device_code == device_id)
            ).first()

        if device is None:
            raise LookupError(f"Device '{device_id}' tidak ditemukan")

        # Resolve sensor
        sd = session.get(SensorDefinition, sensor_def_id)
        if sd is None:
            raise LookupError(f"Sensor Definition ID {sensor_def_id} tidak ditemukan")

        # Check existing mapping
        existing = session.exec(
            select(DeviceSensor)
            .where(DeviceSensor.device_id == device.id)
            .where(DeviceSensor.sensor_def_id == sensor_def_id)
        ).first()

        if existing:
            # Update the existing mapping
            existing.gpio_pin = gpio_pin
            existing.i2c_address = i2c_address
            existing.notes = notes
            existing.updated_at = datetime.now(timezone.utc)
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return _serialize_mapping(existing, sd)

        # Create new mapping
        ds = DeviceSensor(
            device_id=device.id,
            sensor_def_id=sensor_def_id,
            gpio_pin=gpio_pin,
            i2c_address=i2c_address,
            install_date=install_date or date.today(),
            notes=notes,
        )
        session.add(ds)
        session.commit()
        session.refresh(ds)
        return _serialize_mapping(ds, sd)


def list_device_sensors(device_id: str) -> list[dict[str, Any]]:
    """List all sensors installed on a device."""
    with _get_session() as session:
        # Resolve device
        try:
            uid = UUID(device_id)
            device = session.get(Device, uid)
        except ValueError:
            device = session.exec(
                select(Device).where(Device.device_code == device_id)
            ).first()

        if device is None:
            raise LookupError(f"Device '{device_id}' tidak ditemukan")

        stmt = (
            select(DeviceSensor, SensorDefinition)
            .join(SensorDefinition, DeviceSensor.sensor_def_id == SensorDefinition.id)
            .where(DeviceSensor.device_id == device.id)
            .order_by(SensorDefinition.sensor_code)
        )
        rows = session.exec(stmt).all()
        return [_serialize_mapping(ds, sd) for ds, sd in rows]


def unmap_sensor_from_device(mapping_id: int) -> dict[str, Any]:
    """Remove a sensor mapping (uninstall sensor from device)."""
    with _get_session() as session:
        ds = session.get(DeviceSensor, mapping_id)
        if ds is None:
            raise LookupError(f"Mapping ID {mapping_id} tidak ditemukan")

        sd = session.get(SensorDefinition, ds.sensor_def_id)
        data = _serialize_mapping(ds, sd)

        session.delete(ds)
        session.commit()
        return data
