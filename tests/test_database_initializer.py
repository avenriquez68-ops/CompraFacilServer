"""Pruebas de inicialización de la base de datos."""

from sqlalchemy import create_engine, inspect

from app.infrastructure.database.initializer import (
    initialize_database,
)


def test_initialize_database_creates_required_tables() -> None:
    """Debe crear todas las tablas de la aplicación."""

    engine = create_engine("sqlite:///:memory:")

    initialize_database(database_engine=engine)

    table_names = set(inspect(engine).get_table_names())

    assert "search_history" in table_names
    assert "affiliate_clicks" in table_names

    engine.dispose()