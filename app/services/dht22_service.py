from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.core.postgresql import create_db_and_tables, get_postgres_engine
from app.models import DHT22Reading, Device, DustReading, GasReading, HeavyEquipmentReading


def create_database_tables():
    create_db_and_tables()


def create_dht22_table():
    create_database_tables()


def parse_float(payload, field_name):
    value = payload.get(field_name)
    if value is None:
        raise ValueError(f"{field_name} wajib diisi")

    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} harus berupa angka") from exc


def parse_recorded_at(payload):
    value = payload.get("recorded_at")
    if not value:
        return datetime.now(timezone.utc)

    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("recorded_at harus format ISO 8601") from exc


def validate_dht22_payload(payload):
    device_id = str(payload.get("device_id") or payload.get("sensor_code") or "DHT22-001").strip()
    if not device_id:
        raise ValueError("device_id tidak boleh kosong")

    temperature = parse_float(payload, "temperature")
    humidity = parse_float(payload, "humidity")
    recorded_at = parse_recorded_at(payload)

    if not -40 <= temperature <= 80:
        raise ValueError("temperature harus berada di rentang -40 sampai 80 Celsius")
    if not 0 <= humidity <= 100:
        raise ValueError("humidity harus berada di rentang 0 sampai 100 persen")

    return {
        "device_id": device_id,
        "device_name": payload.get("device_name"),
        "location": payload.get("location"),
        "description": payload.get("description"),
        "temperature_c": temperature,
        "humidity_percent": humidity,
        "recorded_at": recorded_at,
    }


def store_dht22_reading(payload):
    reading = validate_dht22_payload(payload)

    with Session(get_postgres_engine()) as session:
        device = session.exec(
            select(Device).where(Device.device_id == reading["device_id"])
        ).first()

        if device is None:
            device = Device(
                device_id=reading["device_id"],
                device_name=reading["device_name"],
                location=reading["location"],
                description=reading["description"],
            )
            session.add(device)
        else:
            if reading["device_name"] is not None:
                device.device_name = reading["device_name"]
            if reading["location"] is not None:
                device.location = reading["location"]
            if reading["description"] is not None:
                device.description = reading["description"]
            device.updated_at = datetime.now()

        row = DHT22Reading(
            device_id=reading["device_id"],
            temperature_c=Decimal(str(reading["temperature_c"])),
            humidity_percent=Decimal(str(reading["humidity_percent"])),
            recorded_at=reading["recorded_at"],
        )
        session.add(row)
        mirrored_rows = create_domain_temperature_rows(reading)
        session.add_all(mirrored_rows)
        session.commit()
        session.refresh(row)

    return {
        "id": row.id,
        "device_id": row.device_id,
        "temperature": float(row.temperature_c),
        "humidity": float(row.humidity_percent),
        "recorded_at": row.recorded_at.isoformat(),
        "created_at": row.created_at.isoformat(),
        "mirrored_to": [
            "tb_debu_tambang",
            "tb_gas_tambang",
            "tb_emisi_alat_berat",
        ],
    }


def create_domain_temperature_rows(reading):
    base_payload = {
        "waktu": reading["recorded_at"],
        "sensor_id": reading["device_id"],
        "lokasi": reading["location"],
        "suhu": Decimal(str(reading["temperature_c"])),
        "kelembaban": Decimal(str(reading["humidity_percent"])),
    }

    return [
        DustReading(**base_payload),
        GasReading(**base_payload),
        HeavyEquipmentReading(**base_payload),
    ]
