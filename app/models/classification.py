from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric, String, Text, text
from sqlmodel import Field, SQLModel


class Classification(SQLModel, table=True):
    __tablename__ = "classifications"

    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    sensor_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("sensors.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        )
    )
    source_type: str = Field(sa_column=Column(String(50), nullable=False, index=True))
    source_reading_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    classification: str = Field(sa_column=Column(String(100), nullable=False))
    risk_level: str = Field(sa_column=Column(String(30), nullable=False, index=True))
    score: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    message: Optional[str] = Field(default=None, sa_column=Column(Text))
    rule_version: Optional[str] = Field(default="v1", sa_column=Column(String(50), server_default=text("'v1'")))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), index=True),
    )
