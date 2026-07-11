"""Sensor reading models (Header-Detail pattern).

Maps to schema tables:
- sensor_readings  (Header — one row per ESP32 payload)
- tb_debu_tambang  (Detail — dust/particulate)
- tb_gas_tambang   (Detail — mine gas)
- tb_emisi_alat_berat (Detail — heavy equipment emission)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlmodel import Field, SQLModel


class SensorReading(SQLModel, table=True):
    """Header table: one row per ESP32 reading payload.

    Contains common ambient data (temperature, humidity from DHT22)
    and device telemetry (battery, wifi, rtc sync status).
    """

    __tablename__ = "sensor_readings"
    __table_args__ = (
        CheckConstraint(
            "temperature IS NULL OR temperature BETWEEN -40 AND 85",
            name="chk_sensor_readings_temperature",
        ),
        CheckConstraint(
            "humidity IS NULL OR humidity BETWEEN 0 AND 100",
            name="chk_sensor_readings_humidity",
        ),
        Index("idx_sensor_readings_device_time", "device_id", "recorded_at"),
        Index("idx_sensor_readings_time", "recorded_at"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    device_id: UUID = Field(
        sa_column=Column(
            PgUUID(as_uuid=True),
            ForeignKey("devices.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    recorded_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    temperature: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(6, 2)))
    humidity: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(6, 2)))
    battery_voltage: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(4, 2)))
    wifi_rssi: Optional[int] = Field(default=None, sa_column=Column(Integer))
    rtc_synced: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("FALSE")),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class DebuTambang(SQLModel, table=True):
    """Detail table: dust/particulate matter readings (PM2.5, PM10)."""

    __tablename__ = "tb_debu_tambang"
    __table_args__ = (
        UniqueConstraint("reading_id", name="uq_debu_tambang_reading"),
        CheckConstraint("pm25 IS NULL OR pm25 >= 0", name="chk_debu_tambang_pm25"),
        CheckConstraint("pm10 IS NULL OR pm10 >= 0", name="chk_debu_tambang_pm10"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    reading_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("sensor_readings.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    pm25: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    pm10: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class GasTambang(SQLModel, table=True):
    """Detail table: mine gas readings (CH4, H2S)."""

    __tablename__ = "tb_gas_tambang"
    __table_args__ = (
        UniqueConstraint("reading_id", name="uq_gas_tambang_reading"),
        CheckConstraint("ch4 IS NULL OR ch4 >= 0", name="chk_gas_tambang_ch4"),
        CheckConstraint("h2s IS NULL OR h2s >= 0", name="chk_gas_tambang_h2s"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    reading_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("sensor_readings.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    ch4: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 4)))
    h2s: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 4)))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class EmisiAlatBerat(SQLModel, table=True):
    """Detail table: heavy equipment emission readings (CO, CO2)."""

    __tablename__ = "tb_emisi_alat_berat"
    __table_args__ = (
        UniqueConstraint("reading_id", name="uq_emisi_alat_berat_reading"),
        CheckConstraint("co IS NULL OR co >= 0", name="chk_emisi_alat_berat_co"),
        CheckConstraint(
            "co2_estimated IS NULL OR co2_estimated >= 0",
            name="chk_emisi_alat_berat_co2",
        ),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    reading_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("sensor_readings.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    co: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 4)))
    co2_estimated: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 4)))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
