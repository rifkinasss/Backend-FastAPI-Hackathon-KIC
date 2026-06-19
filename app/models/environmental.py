from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Column, DateTime, Index, Numeric, String, text
from sqlmodel import Field, SQLModel


class DustReading(SQLModel, table=True):
    __tablename__ = "tb_debu_tambang"
    __table_args__ = (
        Index("idx_tb_debu_tambang_sensor_time", "sensor_id", "waktu"),
        Index("idx_tb_debu_tambang_time", "waktu"),
    )

    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    waktu: datetime = Field(sa_column=Column(DateTime, nullable=False))
    sensor_id: str = Field(sa_column=Column(String(100), nullable=False))
    lokasi: Optional[str] = Field(default=None, sa_column=Column(String(150)))
    pm25: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    pm10: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    suhu: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    kelembaban: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    )


class GasReading(SQLModel, table=True):
    __tablename__ = "tb_gas_tambang"
    __table_args__ = (
        Index("idx_tb_gas_tambang_sensor_time", "sensor_id", "waktu"),
        Index("idx_tb_gas_tambang_time", "waktu"),
    )

    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    waktu: datetime = Field(sa_column=Column(DateTime, nullable=False))
    sensor_id: str = Field(sa_column=Column(String(100), nullable=False))
    lokasi: Optional[str] = Field(default=None, sa_column=Column(String(150)))
    ch4: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    h2s: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    suhu: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    kelembaban: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    )


class HeavyEquipmentReading(SQLModel, table=True):
    __tablename__ = "tb_emisi_alat_berat"
    __table_args__ = (
        Index("idx_tb_emisi_alat_berat_sensor_time", "sensor_id", "waktu"),
        Index("idx_tb_emisi_alat_berat_time", "waktu"),
    )

    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    waktu: datetime = Field(sa_column=Column(DateTime, nullable=False))
    sensor_id: str = Field(sa_column=Column(String(100), nullable=False))
    lokasi: Optional[str] = Field(default=None, sa_column=Column(String(150)))
    co: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    co2: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    suhu: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    kelembaban: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    )
