"""Pruebas del cliente OAuth de Mercado Libre."""

from urllib.parse import parse_qs

import httpx
import pytest

from app.core.config import Settings
from app.infrastructure.clients.mercado_libre_oauth import (
    MercadoLibreOAuthClient,
    MercadoLibreOAuthError,
)


@pytest.mark.asyncio
async def test_exchange_code_requests_mercado_libre_token() -> None:
    """Debe intercambiar el código usando PKCE y datos en el body."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == (
            "https://api.mercadolibre.com/oauth/token"
        )
        assert request.headers["content-type"].startswith(
            "application/x-www-form-urlencoded"
        )

        body = parse_qs(request.content.decode("utf-8"))

        assert body == {
            "grant_type": ["authorization_code"],
            "client_id": ["test-client-id"],
            "client_secret": ["test-client-secret"],
            "code": ["test-authorization-code"],
            "redirect_uri": [
                (
                    "https://api.dameprecio.shop"
                    "/api/v1/auth/mercado-libre/callback"
                )
            ],
            "code_verifier": ["test-code-verifier"],
        }

        return httpx.Response(
            status_code=200,
            json={
                "access_token": "test-access-token",
                "token_type": "Bearer",
                "expires_in": 21600,
                "scope": "offline_access read",
                "user_id": 123456,
                "refresh_token": "test-refresh-token",
            },
        )

    app_settings = Settings(
        _env_file=None,
        mercado_libre_client_id="test-client-id",
        mercado_libre_client_secret="test-client-secret",
        mercado_libre_redirect_uri=(
            "https://api.dameprecio.shop"
            "/api/v1/auth/mercado-libre/callback"
        ),
    )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as http_client:
        oauth_client = MercadoLibreOAuthClient(
            app_settings=app_settings,
            http_client=http_client,
        )

        token = await oauth_client.exchange_code(
            code="test-authorization-code",
            code_verifier="test-code-verifier",
        )

    assert token.access_token == "test-access-token"
    assert token.refresh_token == "test-refresh-token"
    assert token.expires_in == 21600
    assert token.user_id == 123456

@pytest.mark.asyncio
async def test_exchange_code_handles_rejected_request() -> None:
    """Debe traducir un código rechazado a un error controlado."""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=400,
            json={
                "error": "invalid_grant",
                "message": "Authorization code is invalid",
            },
        )

    app_settings = Settings(
        _env_file=None,
        mercado_libre_client_id="test-client-id",
        mercado_libre_client_secret="test-client-secret",
    )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as http_client:
        oauth_client = MercadoLibreOAuthClient(
            app_settings=app_settings,
            http_client=http_client,
        )

        with pytest.raises(
            MercadoLibreOAuthError,
            match="rechazó",
        ):
            await oauth_client.exchange_code(
                code="invalid-code",
                code_verifier="test-code-verifier",
            )