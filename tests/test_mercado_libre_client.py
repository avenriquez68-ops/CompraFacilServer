"""Pruebas del cliente HTTP de Mercado Libre."""

import httpx
import pytest

from app.core.config import Settings
from app.infrastructure.clients.mercado_libre import (
    MercadoLibreClient,
)


class StoredTokenProvider:
    """Proveedor simulado de un token almacenado."""

    async def get_access_token(self) -> str:
        return "stored-access-token"


@pytest.mark.asyncio
async def test_client_uses_stored_access_token() -> None:
    """Debe enviar el token recuperado desde la base de datos."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == (
            "Bearer stored-access-token"
        )

        return httpx.Response(
            status_code=200,
            json={
                "results": [
                    {
                        "id": "MLM123",
                        "title": "Producto de prueba",
                        "price": 1000,
                        "currency_id": "MXN",
                        "permalink": (
                            "https://www.mercadolibre.com.mx"
                            "/producto/MLM123"
                        ),
                        "shipping": {
                            "free_shipping": True,
                        },
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as http_client:
        client = MercadoLibreClient(
            app_settings=Settings(_env_file=None),
            http_client=http_client,
            token_provider=StoredTokenProvider(),
        )

        products = await client.search_products(
            query="laptop",
            limit=10,
        )

    assert len(products) == 1
    assert products[0].id == "MLM123"

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "expected_message"),
    [
        (401, "token de acceso"),
        (403, "permisos"),
    ],
)
async def test_client_distinguishes_authentication_errors(
    status_code: int,
    expected_message: str,
) -> None:
    """Debe diferenciar un token inválido de permisos insuficientes."""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=status_code,
            json={"message": "Request rejected"},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as http_client:
        client = MercadoLibreClient(
            app_settings=Settings(_env_file=None),
            http_client=http_client,
            token_provider=StoredTokenProvider(),
        )

        with pytest.raises(
            Exception,
            match=expected_message,
        ):
            await client.search_products(
                query="laptop",
                limit=5,
            )