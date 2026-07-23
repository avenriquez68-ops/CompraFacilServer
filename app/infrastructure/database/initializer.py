"""Inicialización de las tablas de la aplicación."""

from app.infrastructure.database.connection import Base, engine
from app.models.search_history import SearchHistoryModel


def initialize_database() -> None:
    """Crea las tablas que todavía no existen."""

    Base.metadata.create_all(bind=engine)


__all__ = [
    "SearchHistoryModel",
    "initialize_database",
]