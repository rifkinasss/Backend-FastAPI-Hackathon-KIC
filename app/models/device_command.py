from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Index, String, Text, text
from sqlmodel import Field, SQLModel


class DeviceState(SQLModel, table=True):
    __tablename__ = "device_states"
    __table_args__ = (
        Index("idx_device_states_online", "is_online"),
        Index("idx_device_states_last_seen", "last_seen_at"),
    )

    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    device_id: str = Field(
        sa_column=Column(
            String(100),
            ForeignKey("devices.device_id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        )
    )
    is_online: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("TRUE")))
    power_state: str = Field(default="on", sa_column=Column(String(20), nullable=False, server_default="on"))
    last_seen_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    last_command_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class DeviceCommand(SQLModel, table=True):
    __tablename__ = "device_commands"
    __table_args__ = (
        Index("idx_device_commands_device_status", "device_id", "status"),
        Index("idx_device_commands_created", "created_at"),
    )

    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    device_id: str = Field(
        sa_column=Column(
            String(100),
            ForeignKey("devices.device_id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )
    )
    command: str = Field(sa_column=Column(String(50), nullable=False))
    status: str = Field(default="pending", sa_column=Column(String(30), nullable=False, server_default="pending"))
    requested_by: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
    acknowledged_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
