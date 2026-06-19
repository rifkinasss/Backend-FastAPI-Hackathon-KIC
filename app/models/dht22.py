from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Index, Numeric, String, text
from sqlmodel import Field, SQLModel


class DHT22Reading(SQLModel, table=True):
    __tablename__ = "dht22_readings"
    __table_args__ = (
        CheckConstraint("temperature_c BETWEEN -40 AND 80", name="chk_dht22_temperature"),
        CheckConstraint("humidity_percent BETWEEN 0 AND 100", name="chk_dht22_humidity"),
        Index("idx_dht22_readings_device_time", "device_id", "recorded_at"),
    )

    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    device_id: str = Field(
        sa_column=Column(
            String(100),
            ForeignKey("devices.device_id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False,
        )
    )
    temperature_c: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False))
    humidity_percent: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False))
    recorded_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
