"""Sensor reading routes — data ingestion from ESP32.

Endpoints:
  POST /api/v1/readings              — ESP32 sends sensor payload
  GET  /api/v1/readings              — List recent readings
  GET  /api/v1/readings/{reading_id} — Get single reading detail
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.services.reading_service import (
    get_latest_readings,
    get_reading_by_id,
    store_reading,
)


router = APIRouter(prefix="/api/v1/readings", tags=["Readings"])


# ── Pydantic Schema ──────────────────────────────────────────


class ReadingPayload(BaseModel):
    """Payload yang dikirim ESP32 setiap interval.

    Satu payload = satu pembacaan seluruh sensor.
    Backend akan memisahkan ke header + 3 tabel detail.
    """

    device_code: str = Field(
        ..., min_length=1, max_length=50,
        examples=["ESP32-MINE-001"],
        description="Device code dari ESP32 yang mengirim data.",
    )
    recorded_at: Optional[datetime] = Field(
        default=None,
        examples=["2026-07-11T11:00:00+08:00"],
        description="Timestamp dari RTC device. Jika tidak diisi, server time digunakan.",
    )

    # DHT22 — Ambient (masuk ke header)
    temperature: Optional[float] = Field(
        default=None, examples=[31.5],
        description="Suhu ambient dari DHT22 dalam °C.",
    )
    humidity: Optional[float] = Field(
        default=None, examples=[72.0],
        description="Kelembaban relatif dari DHT22 dalam %.",
    )

    # Device telemetry (masuk ke header)
    battery_voltage: Optional[float] = Field(
        default=None, examples=[3.72],
        description="Tegangan baterai dalam Volt.",
    )
    wifi_rssi: Optional[int] = Field(
        default=None, examples=[-45],
        description="Kekuatan sinyal Wi-Fi dalam dBm.",
    )
    rtc_synced: bool = Field(
        default=False,
        description="Apakah RTC sudah NTP-sync saat pembacaan.",
    )

    # Debu Tambang (PMS5003 — masa depan, bisa null)
    pm25: Optional[float] = Field(
        default=None, examples=[35.0],
        description="PM2.5 dalam µg/m³ (PMS5003).",
    )
    pm10: Optional[float] = Field(
        default=None, examples=[82.0],
        description="PM10 dalam µg/m³ (PMS5003).",
    )

    # Gas Tambang
    ch4: Optional[float] = Field(
        default=None, examples=[450.0],
        description="Metana (CH₄) dalam ppm (MQ4).",
    )
    h2s: Optional[float] = Field(
        default=None, examples=[None],
        description="Hidrogen sulfida (H₂S) dalam ppm (MQ136 — masa depan).",
    )

    # Emisi Alat Berat
    co: Optional[float] = Field(
        default=None, examples=[12.5],
        description="Karbon monoksida (CO) dalam ppm (MQ7).",
    )
    co2_estimated: Optional[float] = Field(
        default=None, examples=[680.0],
        description="Estimasi CO₂ dalam ppm (MQ135).",
    )


# ── Routes ───────────────────────────────────────────────────


@router.post("", status_code=201)
def api_create_reading(payload: ReadingPayload):
    """Terima payload sensor dari ESP32.

    Satu request = satu pembacaan semua sensor.
    Backend otomatis memisahkan data ke:
    - sensor_readings (header)
    - tb_debu_tambang (PM2.5, PM10)
    - tb_gas_tambang (CH4, H2S)
    - tb_emisi_alat_berat (CO, CO2)

    Dan mengupdate status device (online, battery, wifi).
    """
    try:
        result = store_reading(
            device_code=payload.device_code,
            recorded_at=payload.recorded_at,
            temperature=payload.temperature,
            humidity=payload.humidity,
            battery_voltage=payload.battery_voltage,
            wifi_rssi=payload.wifi_rssi,
            rtc_synced=payload.rtc_synced,
            pm25=payload.pm25,
            pm10=payload.pm10,
            ch4=payload.ch4,
            h2s=payload.h2s,
            co=payload.co,
            co2_estimated=payload.co2_estimated,
        )
        return {"message": "Data sensor berhasil disimpan", "data": result}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("")
def api_list_readings(
    device: Optional[str] = Query(None, description="Filter by device_code or UUID"),
    limit: int = Query(20, ge=1, le=100, description="Jumlah data yang dikembalikan"),
):
    """List pembacaan sensor terbaru."""
    try:
        readings = get_latest_readings(device_code=device, limit=limit)
        return {"data": readings, "count": len(readings)}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{reading_id}")
def api_get_reading(reading_id: int):
    """Get detail satu pembacaan beserta semua data sensor."""
    try:
        reading = get_reading_by_id(reading_id)
        return {"data": reading}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
