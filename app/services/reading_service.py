"""Sensor reading service (Header-Detail pattern).

Flow:
  ESP32 payload → sensor_readings (header)
                → tb_debu_tambang (detail)
                → tb_gas_tambang (detail)
                → tb_emisi_alat_berat (detail)
                → device_states (update last_seen)
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from app.core.postgresql import get_postgres_engine
from app.models import (
    DebuTambang,
    Device,
    DeviceState,
    EmisiAlatBerat,
    GasTambang,
    SensorReading,
)


# ── Helpers ──────────────────────────────────────────────────


def _get_session() -> Session:
    return Session(get_postgres_engine())


def _to_decimal(value: float | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _resolve_device(session: Session, device_ref: str) -> Device:
    """Resolve device by UUID or device_code.
    If it doesn't exist, automatically provision the device (Option B).
    """
    try:
        uid = UUID(device_ref)
        device = session.get(Device, uid)
        if device:
            return device
    except ValueError:
        pass

    device = session.exec(
        select(Device).where(Device.device_code == device_ref)
    ).first()

    if device is None:
        # Auto-provision the device
        device = Device(
            device_code=device_ref.strip(),
            device_name=f"Auto Node {device_ref}",
            location="Lokasi Belum Ditentukan",
            description="Otomatis terdaftar dari pengiriman data sensor ESP32",
        )
        session.add(device)
        session.flush()  # dapatkan device.id

        # Auto-create initial state
        state = DeviceState(
            device_id=device.id,
            is_online=True,
            power_state="on",
        )
        session.add(state)
        session.flush()

    return device



def _serialize_reading(
    reading: SensorReading,
    debu: DebuTambang,
    gas: GasTambang,
    emisi: EmisiAlatBerat,
) -> dict[str, Any]:
    return {
        "reading_id": reading.id,
        "device_id": str(reading.device_id),
        "recorded_at": reading.recorded_at.isoformat() if reading.recorded_at else None,
        "temperature": float(reading.temperature) if reading.temperature is not None else None,
        "humidity": float(reading.humidity) if reading.humidity is not None else None,
        "battery_voltage": float(reading.battery_voltage) if reading.battery_voltage is not None else None,
        "wifi_rssi": reading.wifi_rssi,
        "rtc_synced": reading.rtc_synced,
        "created_at": reading.created_at.isoformat() if reading.created_at else None,
        "debu_tambang": {
            "pm25": float(debu.pm25) if debu.pm25 is not None else None,
            "pm10": float(debu.pm10) if debu.pm10 is not None else None,
        },
        "gas_tambang": {
            "ch4": float(gas.ch4) if gas.ch4 is not None else None,
            "h2s": float(gas.h2s) if gas.h2s is not None else None,
        },
        "emisi_alat_berat": {
            "co": float(emisi.co) if emisi.co is not None else None,
            "co2_estimated": float(emisi.co2_estimated) if emisi.co2_estimated is not None else None,
        },
    }


# ── Store Reading ────────────────────────────────────────────


def store_reading(
    *,
    device_code: str,
    recorded_at: datetime | None = None,
    temperature: float | None = None,
    humidity: float | None = None,
    battery_voltage: float | None = None,
    wifi_rssi: int | None = None,
    rtc_synced: bool = False,
    # Debu Tambang
    pm25: float | None = None,
    pm10: float | None = None,
    # Gas Tambang
    ch4: float | None = None,
    h2s: float | None = None,
    # Emisi Alat Berat
    co: float | None = None,
    co2_estimated: float | None = None,
) -> dict[str, Any]:
    """Process one ESP32 payload into header + 3 detail rows.

    1. Create sensor_readings (header)
    2. Create tb_debu_tambang (detail)
    3. Create tb_gas_tambang (detail)
    4. Create tb_emisi_alat_berat (detail)
    5. Update device_states (online + last_seen)
    """

    now = datetime.now(timezone.utc)

    with _get_session() as session:
        # 0. Resolve device
        device = _resolve_device(session, device_code)

        if not device.is_active:
            raise ValueError(f"Device '{device_code}' sudah dinonaktifkan")

        # 1. Header
        reading = SensorReading(
            device_id=device.id,
            recorded_at=recorded_at or now,
            temperature=_to_decimal(temperature),
            humidity=_to_decimal(humidity),
            battery_voltage=_to_decimal(battery_voltage),
            wifi_rssi=wifi_rssi,
            rtc_synced=rtc_synced,
        )
        session.add(reading)
        session.flush()  # get reading.id

        # 2. Detail — Debu Tambang
        debu = DebuTambang(
            reading_id=reading.id,
            pm25=_to_decimal(pm25),
            pm10=_to_decimal(pm10),
        )
        session.add(debu)

        # 3. Detail — Gas Tambang
        gas = GasTambang(
            reading_id=reading.id,
            ch4=_to_decimal(ch4),
            h2s=_to_decimal(h2s),
        )
        session.add(gas)

        # 4. Detail — Emisi Alat Berat
        emisi = EmisiAlatBerat(
            reading_id=reading.id,
            co=_to_decimal(co),
            co2_estimated=_to_decimal(co2_estimated),
        )
        session.add(emisi)

        # 5. Update device state → online
        state = session.exec(
            select(DeviceState).where(DeviceState.device_id == device.id)
        ).first()
        if state:
            state.is_online = True
            state.power_state = "on"
            state.last_seen_at = now
            if battery_voltage is not None:
                state.battery_voltage = _to_decimal(battery_voltage)
            if wifi_rssi is not None:
                state.wifi_rssi = wifi_rssi
            session.add(state)

        session.commit()
        session.refresh(reading)
        session.refresh(debu)
        session.refresh(gas)
        session.refresh(emisi)

        result = _serialize_reading(reading, debu, gas, emisi)
        result["device_code"] = device.device_code
        return result


# ── Get Readings ─────────────────────────────────────────────


def get_latest_readings(
    device_code: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Get recent readings, optionally filtered by device."""

    with _get_session() as session:
        stmt = (
            select(SensorReading)
            .order_by(SensorReading.recorded_at.desc())
            .limit(limit)
        )

        if device_code:
            device = _resolve_device(session, device_code)
            stmt = stmt.where(SensorReading.device_id == device.id)

        readings = session.exec(stmt).all()
        results = []

        for reading in readings:
            debu = session.exec(
                select(DebuTambang).where(DebuTambang.reading_id == reading.id)
            ).first()
            gas = session.exec(
                select(GasTambang).where(GasTambang.reading_id == reading.id)
            ).first()
            emisi = session.exec(
                select(EmisiAlatBerat).where(EmisiAlatBerat.reading_id == reading.id)
            ).first()

            if debu and gas and emisi:
                data = _serialize_reading(reading, debu, gas, emisi)
                # Get device_code
                device = session.get(Device, reading.device_id)
                if device:
                    data["device_code"] = device.device_code
                results.append(data)

        return results


def get_reading_by_id(reading_id: int) -> dict[str, Any]:
    """Get a single reading with all details."""

    with _get_session() as session:
        reading = session.get(SensorReading, reading_id)
        if reading is None:
            raise LookupError(f"Reading ID {reading_id} tidak ditemukan")

        debu = session.exec(
            select(DebuTambang).where(DebuTambang.reading_id == reading.id)
        ).first()
        gas = session.exec(
            select(GasTambang).where(GasTambang.reading_id == reading.id)
        ).first()
        emisi = session.exec(
            select(EmisiAlatBerat).where(EmisiAlatBerat.reading_id == reading.id)
        ).first()

        if not debu or not gas or not emisi:
            raise LookupError(f"Detail untuk Reading ID {reading_id} tidak lengkap")

        data = _serialize_reading(reading, debu, gas, emisi)
        device = session.get(Device, reading.device_id)
        if device:
            data["device_code"] = device.device_code
        return data
