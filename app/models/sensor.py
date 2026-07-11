"""Sensor catalog models (extensible — no migration for new sensors).

Maps to schema tables:
- sensor_definitions
- sensor_parameters
- device_sensors
- calibration_profiles
- sensor_thresholds
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlmodel import Field, SQLModel


class SensorDefinition(SQLModel, table=True):
    """Master catalog of sensor types (DHT22, MQ4, PMS5003, etc)."""

    __tablename__ = "sensor_definitions"
    __table_args__ = (
        UniqueConstraint("sensor_code", name="uq_sensor_definitions_code"),
        CheckConstraint(
            "interface_type IN ('analog', 'digital', 'i2c', 'spi', 'uart', 'onewire')",
            name="chk_sensor_definitions_interface",
        ),
        Index("idx_sensor_definitions_active", "is_active"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    sensor_code: str = Field(sa_column=Column(String(50), nullable=False))
    sensor_name: str = Field(sa_column=Column(String(150), nullable=False))
    manufacturer: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    interface_type: Optional[str] = Field(default=None, sa_column=Column(String(30)))
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("TRUE")),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class SensorParameter(SQLModel, table=True):
    """Parameters measured by each sensor type."""

    __tablename__ = "sensor_parameters"
    __table_args__ = (
        UniqueConstraint("sensor_def_id", "parameter_code", name="uq_sensor_parameters_code"),
        CheckConstraint(
            "precision_dp BETWEEN 0 AND 8",
            name="chk_sensor_parameters_precision",
        ),
        CheckConstraint(
            "min_value IS NULL OR max_value IS NULL OR min_value <= max_value",
            name="chk_sensor_parameters_range",
        ),
        Index("idx_sensor_parameters_def", "sensor_def_id"),
        Index("idx_sensor_parameters_code", "parameter_code"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    sensor_def_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("sensor_definitions.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    parameter_code: str = Field(sa_column=Column(String(50), nullable=False))
    parameter_name: str = Field(sa_column=Column(String(100), nullable=False))
    unit: Optional[str] = Field(default=None, sa_column=Column(String(30)))
    min_value: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 4)))
    max_value: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 4)))
    precision_dp: int = Field(
        default=2,
        sa_column=Column(SmallInteger, nullable=False, server_default=text("2")),
    )
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class DeviceSensor(SQLModel, table=True):
    """Maps which sensors are physically installed on each device (GPIO/I2C)."""

    __tablename__ = "device_sensors"
    __table_args__ = (
        UniqueConstraint("device_id", "sensor_def_id", name="uq_device_sensors_mapping"),
        Index("idx_device_sensors_device", "device_id"),
        Index("idx_device_sensors_def", "sensor_def_id"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    device_id: UUID = Field(
        sa_column=Column(
            PgUUID(as_uuid=True),
            ForeignKey("devices.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    sensor_def_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("sensor_definitions.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    gpio_pin: Optional[str] = Field(default=None, sa_column=Column(String(20)))
    i2c_address: Optional[str] = Field(default=None, sa_column=Column(String(10)))
    install_date: Optional[date] = Field(default=None, sa_column=Column(Date))
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("TRUE")),
    )
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class CalibrationProfile(SQLModel, table=True):
    """Calibration profiles for MQ-series and other analog sensors."""

    __tablename__ = "calibration_profiles"
    __table_args__ = (
        Index("idx_calibration_profiles_def", "sensor_def_id"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    sensor_def_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("sensor_definitions.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    profile_name: str = Field(sa_column=Column(String(100), nullable=False))
    r0: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 6)))
    slope: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 6)))
    offset: Optional[Decimal] = Field(
        default=None,
        sa_column=Column("offset", Numeric(12, 6)),
    )
    calibrated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    calibrated_by: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("TRUE")),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class SensorThreshold(SQLModel, table=True):
    """Warning/danger/critical thresholds per parameter. Used by AI/Fuzzy."""

    __tablename__ = "sensor_thresholds"
    __table_args__ = (
        UniqueConstraint("parameter_code", name="uq_sensor_thresholds_param"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    parameter_code: str = Field(sa_column=Column(String(50), nullable=False))
    parameter_name: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    unit: Optional[str] = Field(default=None, sa_column=Column(String(30)))
    warning_min: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 4)))
    warning_max: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 4)))
    danger_min: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 4)))
    danger_max: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 4)))
    critical_min: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 4)))
    critical_max: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 4)))
    source: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
