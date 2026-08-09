"""Administración de tokens de acceso de Mercado Libre."""

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Protocol

from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.infrastructure.clients.mercado_libre_oauth import (
    MercadoLibreOAuthClient,
    MercadoLibreOAuthError,
    MercadoLibreToken,
)
from app.infrastructure.database.connection import SessionLocal
from app.repositories.mercado_libre_credential import (
    MercadoLibreCredentialRepository,
    mercado_libre_credential_repository,
)


class OAuthClientProtocol(Protocol):
    """Contrato mínimo del cliente utilizado para renovar tokens."""

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> MercadoLibreToken:
        """Renueva las credenciales de Mercado Libre."""


class MercadoLibreTokenService:
    """Obtiene y renueva el token almacenado."""

    def __init__(
        self,
        repository: MercadoLibreCredentialRepository = (
            mercado_libre_credential_repository
        ),
        oauth_client: OAuthClientProtocol | None = None,
        session_factory: Callable[[], Session] = SessionLocal,
        app_settings: Settings = settings,
    ) -> None:
        self._repository = repository
        self._oauth_client = (
            oauth_client
            if oauth_client is not None
            else MercadoLibreOAuthClient(
                app_settings=app_settings
            )
        )
        self._session_factory = session_factory
        self._settings = app_settings

    async def get_access_token(self) -> str:
        """Devuelve un token vigente o lo renueva."""

        with self._session_factory() as session:
            credential = self._repository.get_latest(
                session=session,
            )

            if credential is None:
                fallback_token = (
                    self._settings.mercado_libre_access_token.strip()
                )

                if fallback_token:
                    return fallback_token

                raise MercadoLibreOAuthError(
                    "Mercado Libre no está conectado."
                )

            expires_at = credential.expires_at

            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(
                    tzinfo=timezone.utc
                )

            renewal_limit = (
                datetime.now(timezone.utc)
                + timedelta(minutes=5)
            )

            if expires_at > renewal_limit:
                return credential.access_token

            token = (
                await self._oauth_client.refresh_access_token(
                    refresh_token=credential.refresh_token,
                )
            )

            self._repository.save(
                session=session,
                token=token,
            )

            return token.access_token


mercado_libre_token_service = MercadoLibreTokenService()