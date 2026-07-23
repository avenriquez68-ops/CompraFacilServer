"""Modelo que representa una búsqueda guardada."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.connection import Base


class SearchHistoryModel(Base):
    """Registro de una búsqueda realizada por el usuario."""

    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    query: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    total_results: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    fallback_used: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )