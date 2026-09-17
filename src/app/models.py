import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column
from uuid_extensions import uuid7

from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )
    request_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
    )

    features: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    churn: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
