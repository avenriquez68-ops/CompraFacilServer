"""Configuración de la conexión con la base de datos."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Clase base de todos los modelos de la base de datos."""


connect_args: dict[str, object] = {}

if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False


engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_database_session() -> Generator[Session, None, None]:
    """Proporciona una sesión y garantiza que se cierre."""

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()