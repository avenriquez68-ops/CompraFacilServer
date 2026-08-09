"""Cliente HTTP para autenticación OAuth con Mercado Libre."""

from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings, settings


@dataclass(frozen=True, slots=True)
class MercadoLibreToken:
    """Tokens devueltos por Mercado Libre."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    scope: str
    user_id: int

class MercadoLibreOAuthError(Exception):
    """Error seguro durante la autenticación con Mercado Libre."""

class MercadoLibreOAuthClient:
    """Intercambia códigos OAuth por tokens de acceso."""

    def __init__(
        self,
        app_settings: Settings = settings,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = app_settings
        self._http_client = http_client

    async def exchange_code(
        self,
        code: str,
        code_verifier: str,
    ) -> MercadoLibreToken:
        """Intercambia un código de autorización usando PKCE."""

        data = {
            "grant_type": "authorization_code",
            "client_id": self._settings.mercado_libre_client_id,
            "client_secret": (
                self._settings.mercado_libre_client_secret
            ),
            "code": code,
            "redirect_uri": (
                self._settings.mercado_libre_redirect_uri
            ),
            "code_verifier": code_verifier,
        }

        try:
            response = await self._post_token_request(data)
            response.raise_for_status()

            payload = response.json()

            return MercadoLibreToken(
                access_token=str(payload["access_token"]),
                refresh_token=str(payload["refresh_token"]),
                token_type=str(payload["token_type"]),
                expires_in=int(payload["expires_in"]),
                scope=str(payload.get("scope", "")),
                user_id=int(payload["user_id"]),
            )

        except httpx.HTTPStatusError as error:
            raise MercadoLibreOAuthError(
                "Mercado Libre rechazó la autorización."
            ) from error

        except httpx.RequestError as error:
            raise MercadoLibreOAuthError(
                "No fue posible comunicarse con Mercado Libre."
            ) from error

        except (KeyError, TypeError, ValueError) as error:
            raise MercadoLibreOAuthError(
                "Mercado Libre devolvió una respuesta inválida."
            ) from error

    async def _post_token_request(
        self,
        data: dict[str, Any],
    ) -> httpx.Response:
        """Realiza la solicitud HTTP al endpoint de tokens."""

        if self._http_client is not None:
            return await self._http_client.post(
                self._settings.mercado_libre_token_url,
                data=data,
                headers={
                    "Accept": "application/json",
                },
            )

        async with httpx.AsyncClient(
            timeout=self._settings.mercado_libre_timeout_seconds,
        ) as client:
            return await client.post(
                self._settings.mercado_libre_token_url,
                data=data,
                headers={
                    "Accept": "application/json",
                },
            )