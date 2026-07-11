"""AI classification and process log models.

Maps to schema tables:
- classifications
- ai_process_logs
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Classification(SQLModel, table=True):
    """AI/Fuzzy classification result per reading per category."""

    __tablename__ = "classifications"
    __table_args__ = (
        UniqueConstraint("reading_id", "category", name="uq_classifications_reading_category"),
        CheckConstraint(
            "category IN ('debu_tambang', 'gas_tambang', 'emisi_alat_berat')",
            name="chk_classifications_category",
        ),
        CheckConstraint(
            "risk_level IN ('aman', 'perhatian', 'warning', 'danger', 'critical')",
            name="chk_classifications_risk_level",
        ),
        CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="chk_classifications_confidence",
        ),
        Index("idx_classifications_reading", "reading_id"),
        Index("idx_classifications_category", "category"),
        Index("idx_classifications_risk_level", "risk_level"),
        Index("idx_classifications_processed", "processed_at"),
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
    category: str = Field(sa_column=Column(String(50), nullable=False))
    classification: str = Field(sa_column=Column(String(100), nullable=False))
    risk_level: str = Field(sa_column=Column(String(30), nullable=False))
    confidence: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 4)))
    score: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 4)))
    message: Optional[str] = Field(default=None, sa_column=Column(Text))
    model_name: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    model_version: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    processed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class AIProcessLog(SQLModel, table=True):
    """Telemetry log for AI/Fuzzy processing runs."""

    __tablename__ = "ai_process_logs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('success', 'failed', 'timeout', 'skipped')",
            name="chk_ai_process_logs_status",
        ),
        CheckConstraint(
            "duration_ms IS NULL OR duration_ms >= 0",
            name="chk_ai_process_logs_duration",
        ),
        Index("idx_ai_process_logs_reading", "reading_id"),
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
    model_name: str = Field(sa_column=Column(String(100), nullable=False))
    model_version: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    duration_ms: Optional[int] = Field(default=None, sa_column=Column(Integer))
    status: str = Field(
        default="success",
        sa_column=Column(String(30), nullable=False, server_default=text("'success'")),
    )
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    input_snapshot: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    output_snapshot: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    processed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
