"""Modelo que representa un clic en un enlace afiliado."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.connection import Base


class AffiliateClickModel(Base):
    """Registro de una redirección hacia una tienda externa."""

    __tablename__ = "affiliate_clicks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    provider_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    product_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    destination_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )