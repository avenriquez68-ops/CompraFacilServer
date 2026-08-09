"""Pruebas HTTP de autenticación con Mercado Libre."""

from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.core.config import settings
from app.main import app

from types import SimpleNamespace

from app.api.dependencies import (
    get_mercado_libre_credential_repository,
    get_mercado_libre_oauth_client,
)
from app.infrastructure.clients.mercado_libre_oauth import (
    MercadoLibreToken,
)
from app.infrastructure.database.connection import (
    get_database_session,
)

client = TestClient(app)


def test_mercado_libre_login_redirects_with_pkce(
    monkeypatch: MonkeyPatch,
) -> None:
    """Debe iniciar OAuth usando state y PKCE S256."""

    monkeypatch.setattr(
        settings,
        "mercado_libre_client_id",
        "test-client-id",
    )
    monkeypatch.setattr(
        settings,
        "mercado_libre_client_secret",
        "test-client-secret",
    )
    monkeypatch.setattr(
        settings,
        "mercado_libre_authorization_url",
        "https://auth.mercadolibre.com.mx/authorization",
    )
    monkeypatch.setattr(
        settings,
        "mercado_libre_redirect_uri",
        (
            "https://api.dameprecio.shop"
            "/api/v1/auth/mercado-libre/callback"
        ),
    )

    response = client.get(
        "/api/v1/auth/mercado-libre/login",
        follow_redirects=False,
    )

    assert response.status_code == 307

    location = urlparse(response.headers["location"])
    parameters = parse_qs(location.query)

    assert location.scheme == "https"
    assert location.netloc == "auth.mercadolibre.com.mx"
    assert location.path == "/authorization"

    assert parameters["response_type"] == ["code"]
    assert parameters["client_id"] == ["test-client-id"]
    assert parameters["redirect_uri"] == [
        (
            "https://api.dameprecio.shop"
            "/api/v1/auth/mercado-libre/callback"
        )
    ]
    assert parameters["code_challenge_method"] == ["S256"]

    state = parameters["state"][0]
    code_challenge = parameters["code_challenge"][0]

    assert len(state) >= 32
    assert len(code_challenge) >= 43
    assert response.cookies["ml_oauth_state"] == state
    assert len(response.cookies["ml_pkce_verifier"]) >= 43

def test_mercado_libre_callback_rejects_invalid_state() -> None:
    """Debe rechazar respuestas que no pertenezcan al login iniciado."""

    response = client.get(
        "/api/v1/auth/mercado-libre/callback",
        params={
            "code": "test-authorization-code",
            "state": "incorrect-state",
        },
        headers={
            "cookie": (
                "ml_oauth_state=expected-state; "
                "ml_pkce_verifier=test-code-verifier"
            ),
        },
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert "state" in response.json()["detail"].lower()

def test_mercado_libre_callback_saves_tokens() -> None:
    """Debe guardar los tokens sin exponerlos al navegador."""

    captured: dict[str, object] = {}

    class FakeOAuthClient:
        async def exchange_code(
            self,
            code: str,
            code_verifier: str,
        ) -> MercadoLibreToken:
            captured["code"] = code
            captured["code_verifier"] = code_verifier

            return MercadoLibreToken(
                access_token="secret-access-token",
                refresh_token="secret-refresh-token",
                token_type="Bearer",
                expires_in=21600,
                scope="offline_access read",
                user_id=123456,
            )

    class FakeCredentialRepository:
        def save(
            self,
            session: object,
            token: MercadoLibreToken,
        ) -> SimpleNamespace:
            captured["session"] = session
            captured["token"] = token

            return SimpleNamespace(
                user_id=token.user_id,
            )

    database_session = object()

    def override_database_session() -> object:
        yield database_session

    def override_oauth_client() -> FakeOAuthClient:
        return FakeOAuthClient()

    def override_repository() -> FakeCredentialRepository:
        return FakeCredentialRepository()

    app.dependency_overrides[
        get_database_session
    ] = override_database_session
    app.dependency_overrides[
        get_mercado_libre_oauth_client
    ] = override_oauth_client
    app.dependency_overrides[
        get_mercado_libre_credential_repository
    ] = override_repository

    try:
        response = client.get(
            "/api/v1/auth/mercado-libre/callback",
            params={
                "code": "test-authorization-code",
                "state": "expected-state",
            },
            headers={
                "cookie": (
                    "ml_oauth_state=expected-state; "
                    "ml_pkce_verifier=test-code-verifier"
                ),
            },
            follow_redirects=False,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "connected",
        "provider_id": "mercado_libre",
        "user_id": 123456,
    }

    assert captured["code"] == "test-authorization-code"
    assert captured["code_verifier"] == "test-code-verifier"
    assert captured["session"] is database_session

    response_text = response.text

    assert "secret-access-token" not in response_text
    assert "secret-refresh-token" not in response_text

    cookie_headers = response.headers.get_list("set-cookie")

    assert any(
        "ml_oauth_state=" in header
        and "Max-Age=0" in header
        for header in cookie_headers
    )
    assert any(
        "ml_pkce_verifier=" in header
        and "Max-Age=0" in header
        for header in cookie_headers
    )

def test_mercado_libre_login_requires_complete_config(
    monkeypatch: MonkeyPatch,
) -> None:
    """Debe rechazar una configuración OAuth incompleta."""

    monkeypatch.setattr(
        settings,
        "mercado_libre_client_id",
        "test-client-id",
    )
    monkeypatch.setattr(
        settings,
        "mercado_libre_client_secret",
        "",
    )

    response = client.get(
        "/api/v1/auth/mercado-libre/login",
        follow_redirects=False,
    )

    assert response.status_code == 503
    assert "configurada" in response.json()["detail"].lower()