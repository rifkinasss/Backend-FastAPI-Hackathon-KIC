"""Device management models.

Maps to schema tables:
- devices
- device_configs
- device_states
- device_commands
- device_logs
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
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlmodel import Field, SQLModel


class Device(SQLModel, table=True):
    """ESP32 IoT device registry. UUID primary key."""

    __tablename__ = "devices"
    __table_args__ = (
        UniqueConstraint("device_code", name="uq_devices_code"),
        Index("idx_devices_active", "is_active"),
    )

    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PgUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        ),
    )
    device_code: str = Field(sa_column=Column(String(50), nullable=False))
    hardware_id: Optional[str] = Field(default=None, sa_column=Column(String(64), unique=True))
    device_name: str = Field(sa_column=Column(String(150), nullable=False))
    location: Optional[str] = Field(default=None, sa_column=Column(String(200)))
    latitude: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 7)))
    longitude: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 7)))
    firmware_ver: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("TRUE")),
    )
    provisioning_status: str = Field(
        default="approved",
        sa_column=Column(String(20), nullable=False, server_default=text("'approved'")),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class DeviceConfig(SQLModel, table=True):
    """Key-value + JSONB configuration store per device."""

    __tablename__ = "device_configs"
    __table_args__ = (
        UniqueConstraint("device_id", "config_key", name="uq_device_configs_key"),
        Index("idx_device_configs_device", "device_id"),
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
    config_key: str = Field(sa_column=Column(String(100), nullable=False))
    config_value: Optional[str] = Field(default=None, sa_column=Column(Text))
    config_json: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
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


class DeviceState(SQLModel, table=True):
    """Real-time operational state per device. One row per device."""

    __tablename__ = "device_states"
    __table_args__ = (
        UniqueConstraint("device_id", name="uq_device_states_device"),
        CheckConstraint(
            "power_state IN ('on', 'off', 'sleep', 'error')",
            name="chk_device_states_power_state",
        ),
        Index("idx_device_states_online", "is_online"),
        Index("idx_device_states_last_seen", "last_seen_at"),
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
    is_online: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("FALSE")),
    )
    power_state: str = Field(
        default="off",
        sa_column=Column(String(20), nullable=False, server_default=text("'off'")),
    )
    battery_voltage: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(4, 2)))
    wifi_rssi: Optional[int] = Field(default=None, sa_column=Column(Integer))
    uptime_seconds: Optional[int] = Field(default=None, sa_column=Column(BigInteger))
    last_seen_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    last_boot_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    last_command_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class DeviceCommand(SQLModel, table=True):
    """Command queue for device remote control."""

    __tablename__ = "device_commands"
    __table_args__ = (
        CheckConstraint(
            "command IN ("
            "'turn_on', 'turn_off', 'restart', 'sleep', "
            "'update_config', 'ota_update', 'calibrate', "
            "'factory_reset', 'diagnostic')",
            name="chk_device_commands_command",
        ),
        CheckConstraint(
            "status IN ("
            "'pending', 'sent', 'acknowledged', "
            "'executed', 'failed', 'expired')",
            name="chk_device_commands_status",
        ),
        Index("idx_device_commands_device_status", "device_id", "status"),
        Index("idx_device_commands_created", "created_at"),
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
    command: str = Field(sa_column=Column(String(50), nullable=False))
    payload: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    status: str = Field(
        default="pending",
        sa_column=Column(String(30), nullable=False, server_default=text("'pending'")),
    )
    requested_by: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
    acknowledged_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    executed_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    expires_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class DeviceLog(SQLModel, table=True):
    """Chronological event log per device."""

    __tablename__ = "device_logs"
    __table_args__ = (
        CheckConstraint(
            "log_level IN ('debug', 'info', 'warning', 'error', 'critical')",
            name="chk_device_logs_level",
        ),
        Index("idx_device_logs_device_time", "device_id", "recorded_at"),
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
    log_level: str = Field(
        default="info",
        sa_column=Column(String(20), nullable=False, server_default=text("'info'")),
    )
    event_type: str = Field(sa_column=Column(String(50), nullable=False))
    message: Optional[str] = Field(default=None, sa_column=Column(Text))
    metadata_: Optional[dict] = Field(
        default=None,
        sa_column=Column("metadata", JSONB),
    )
    recorded_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
