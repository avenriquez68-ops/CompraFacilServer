"""Inicialización de las tablas de la base de datos."""

from sqlalchemy.engine import Engine

from app.infrastructure.database.connection import Base, engine
from app.models import (
    affiliate_click,
    mercado_libre_credential,
    search_history,
)


def initialize_database(
    database_engine: Engine = engine,
) -> None:
    """Crea las tablas que todavía no existen."""

    _ = affiliate_click
    _ = mercado_libre_credential
    _ = search_history

    Base.metadata.create_all(
        bind=database_engine,
    )