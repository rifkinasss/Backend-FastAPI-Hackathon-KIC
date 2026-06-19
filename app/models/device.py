from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text, text
from sqlmodel import Field, SQLModel


class Device(SQLModel, table=True):
    __tablename__ = "devices"

    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    device_name: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    location: Optional[str] = Field(default=None, sa_column=Column(String(150)))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP")),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP")),
    )
