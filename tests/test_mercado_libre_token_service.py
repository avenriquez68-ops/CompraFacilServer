"""Pruebas del servicio de tokens de Mercado Libre."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.infrastructure.clients.mercado_libre_oauth import (
    MercadoLibreToken,
)
from app.infrastructure.database.connection import Base
from app.models.mercado_libre_credential import (
    MercadoLibreCredentialModel,
)
from app.repositories.mercado_libre_credential import (
    MercadoLibreCredentialRepository,
)
from app.services.mercado_libre_token import (
    MercadoLibreTokenService,
)
import pytest

class UnexpectedOAuthClient:
    """Cliente que falla si se intenta renovar el token."""

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> MercadoLibreToken:
        raise AssertionError(
            "No debía renovarse un token vigente."
        )


def create_session_factory() -> tuple[object, object]:
    """Crea sesiones sobre una base temporal."""

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    factory = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    return factory, engine

@pytest.mark.asyncio
async def test_service_returns_valid_saved_token() -> None:
    """Debe usar el access token almacenado si sigue vigente."""

    session_factory, engine = create_session_factory()

    with session_factory() as session:
        credential = MercadoLibreCredentialModel(
            user_id=123456,
            access_token="valid-access-token",
            refresh_token="valid-refresh-token",
            token_type="Bearer",
            scope="offline_access read",
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(hours=2)
            ),
        )

        session.add(credential)
        session.commit()

    service = MercadoLibreTokenService(
        repository=MercadoLibreCredentialRepository(),
        oauth_client=UnexpectedOAuthClient(),
        session_factory=session_factory,
        app_settings=Settings(_env_file=None),
    )

    access_token = await service.get_access_token()

    assert access_token == "valid-access-token"

    engine.dispose()

@pytest.mark.asyncio
async def test_service_refreshes_expired_token() -> None:
    """Debe renovar y guardar un token próximo a vencer."""

    session_factory, engine = create_session_factory()
    captured: dict[str, str] = {}

    class RefreshingOAuthClient:
        async def refresh_access_token(
            self,
            refresh_token: str,
        ) -> MercadoLibreToken:
            captured["refresh_token"] = refresh_token

            return MercadoLibreToken(
                access_token="renewed-access-token",
                refresh_token="renewed-refresh-token",
                token_type="Bearer",
                expires_in=21600,
                scope="offline_access read",
                user_id=123456,
            )

    with session_factory() as session:
        credential = MercadoLibreCredentialModel(
            user_id=123456,
            access_token="expired-access-token",
            refresh_token="current-refresh-token",
            token_type="Bearer",
            scope="offline_access read",
            expires_at=(
                datetime.now(timezone.utc)
                - timedelta(minutes=1)
            ),
        )

        session.add(credential)
        session.commit()

    repository = MercadoLibreCredentialRepository()

    service = MercadoLibreTokenService(
        repository=repository,
        oauth_client=RefreshingOAuthClient(),
        session_factory=session_factory,
        app_settings=Settings(_env_file=None),
    )

    access_token = await service.get_access_token()

    assert access_token == "renewed-access-token"
    assert (
        captured["refresh_token"]
        == "current-refresh-token"
    )

    with session_factory() as session:
        saved_credential = repository.get_latest(
            session=session,
        )

        assert saved_credential is not None
        assert (
            saved_credential.access_token
            == "renewed-access-token"
        )
        assert (
            saved_credential.refresh_token
            == "renewed-refresh-token"
        )

    engine.dispose()