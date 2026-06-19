from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, DateTime, Numeric, String, text
from sqlmodel import Field, SQLModel


class Sensor(SQLModel, table=True):
    __tablename__ = "sensors"

    id: Optional[int] = Field(default=None, primary_key=True)
    sensor_code: str = Field(sa_column=Column(String(50), nullable=False, unique=True))
    name: str = Field(sa_column=Column(String(150), nullable=False))
    category: str = Field(sa_column=Column(String(50), nullable=False, index=True))
    location_name: Optional[str] = Field(default=None, sa_column=Column(String(150)))
    latitude: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 7)))
    longitude: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 7)))
    status: str = Field(default="active", sa_column=Column(String(30), nullable=False, index=True))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    )
