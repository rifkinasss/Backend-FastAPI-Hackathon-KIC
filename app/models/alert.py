"""Alert and notification models.

Maps to schema tables:
- alerts
- notification_logs
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlmodel import Field, SQLModel


class Alert(SQLModel, table=True):
    """Alert records triggered by dangerous classifications."""

    __tablename__ = "alerts"
    __table_args__ = (
        CheckConstraint(
            "severity IS NULL OR severity IN ('low', 'medium', 'high', 'critical')",
            name="chk_alerts_severity",
        ),
        CheckConstraint(
            "status IN ('open', 'acknowledged', 'resolved', 'escalated', 'expired')",
            name="chk_alerts_status",
        ),
        Index("idx_alerts_status", "status"),
        Index("idx_alerts_device_status", "device_id", "status"),
        Index("idx_alerts_classification", "classification_id"),
        Index("idx_alerts_created", "created_at"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    classification_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("classifications.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    device_id: UUID = Field(
        sa_column=Column(
            PgUUID(as_uuid=True),
            ForeignKey("devices.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    alert_type: str = Field(
        default="threshold",
        sa_column=Column(String(50), nullable=False, server_default=text("'threshold'")),
    )
    severity: Optional[str] = Field(default=None, sa_column=Column(String(30)))
    status: str = Field(
        default="open",
        sa_column=Column(String(30), nullable=False, server_default=text("'open'")),
    )
    message: Optional[str] = Field(default=None, sa_column=Column(Text))
    acknowledged_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    acknowledged_by: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    resolved_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    resolved_by: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class NotificationLog(SQLModel, table=True):
    """Audit log of every notification attempt across all channels."""

    __tablename__ = "notification_logs"
    __table_args__ = (
        CheckConstraint(
            "channel IN ('email', 'sms', 'push', 'webhook', 'telegram', 'whatsapp')",
            name="chk_notification_logs_channel",
        ),
        CheckConstraint(
            "status IN ('pending', 'sent', 'delivered', 'failed', 'bounced')",
            name="chk_notification_logs_status",
        ),
        CheckConstraint("retry_count >= 0", name="chk_notification_logs_retry"),
        Index("idx_notification_logs_alert", "alert_id"),
        Index("idx_notification_logs_status", "status"),
        Index("idx_notification_logs_channel", "channel", "status"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    alert_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            ForeignKey("alerts.id", onupdate="CASCADE", ondelete="SET NULL"),
        ),
    )
    channel: str = Field(sa_column=Column(String(30), nullable=False))
    recipient: str = Field(sa_column=Column(String(200), nullable=False))
    subject: Optional[str] = Field(default=None, sa_column=Column(String(300)))
    body: Optional[str] = Field(default=None, sa_column=Column(Text))
    status: str = Field(
        default="pending",
        sa_column=Column(String(30), nullable=False, server_default=text("'pending'")),
    )
    response: Optional[str] = Field(default=None, sa_column=Column(Text))
    retry_count: int = Field(
        default=0,
        sa_column=Column(SmallInteger, nullable=False, server_default=text("0")),
    )
    sent_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
