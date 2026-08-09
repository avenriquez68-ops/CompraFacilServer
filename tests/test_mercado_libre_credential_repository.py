"""Pruebas del repositorio de credenciales de Mercado Libre."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infrastructure.clients.mercado_libre_oauth import (
    MercadoLibreToken,
)
from app.infrastructure.database.connection import Base
from app.repositories.mercado_libre_credential import (
    MercadoLibreCredentialRepository,
)


def create_test_session() -> tuple[Session, object]:
    """Crea una base de datos temporal en memoria."""

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    return Session(engine), engine


def test_repository_saves_mercado_libre_credentials() -> None:
    """Debe guardar los tokens sin devolverlos mediante la API."""

    session, engine = create_test_session()
    repository = MercadoLibreCredentialRepository()

    token = MercadoLibreToken(
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        token_type="Bearer",
        expires_in=21600,
        scope="offline_access read",
        user_id=123456,
    )

    saved_credential = repository.save(
        session=session,
        token=token,
    )

    assert saved_credential.id is not None
    assert saved_credential.user_id == 123456
    assert saved_credential.access_token == "test-access-token"
    assert saved_credential.refresh_token == "test-refresh-token"
    assert saved_credential.expires_at is not None

    session.close()
    engine.dispose()

def test_repository_updates_existing_credentials() -> None:
    """Debe reemplazar los tokens anteriores del mismo usuario."""

    session, engine = create_test_session()
    repository = MercadoLibreCredentialRepository()

    first_token = MercadoLibreToken(
        access_token="first-access-token",
        refresh_token="first-refresh-token",
        token_type="Bearer",
        expires_in=21600,
        scope="offline_access read",
        user_id=123456,
    )

    first_credential = repository.save(
        session=session,
        token=first_token,
    )

    second_token = MercadoLibreToken(
        access_token="second-access-token",
        refresh_token="second-refresh-token",
        token_type="Bearer",
        expires_in=21600,
        scope="offline_access read",
        user_id=123456,
    )

    second_credential = repository.save(
        session=session,
        token=second_token,
    )

    assert second_credential.id == first_credential.id
    assert (
        second_credential.access_token
        == "second-access-token"
    )
    assert (
        second_credential.refresh_token
        == "second-refresh-token"
    )

    session.close()
    engine.dispose()

def test_repository_gets_saved_credentials() -> None:
    """Debe recuperar las credenciales almacenadas."""

    session, engine = create_test_session()
    repository = MercadoLibreCredentialRepository()

    token = MercadoLibreToken(
        access_token="saved-access-token",
        refresh_token="saved-refresh-token",
        token_type="Bearer",
        expires_in=21600,
        scope="offline_access read",
        user_id=123456,
    )

    repository.save(
        session=session,
        token=token,
    )

    credential = repository.get_latest(
        session=session,
    )

    assert credential is not None
    assert credential.user_id == 123456
    assert credential.access_token == "saved-access-token"
    assert credential.refresh_token == "saved-refresh-token"

    session.close()
    engine.dispose()