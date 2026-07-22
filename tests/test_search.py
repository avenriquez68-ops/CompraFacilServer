"""Pruebas del endpoint de búsqueda."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.infrastructure.clients.mercado_libre import MercadoLibreClient
from app.main import app
from app.services.product_search import ProductSearchService

client = TestClient(app)


def test_search_query_requires_two_characters() -> None:
    """La consulta debe tener al menos dos caracteres."""

    response = client.get(
        "/api/v1/search",
        params={"q": "a"},
    )

    assert response.status_code == 422


def test_search_limit_cannot_exceed_fifty() -> None:
    """El límite máximo permitido es 50."""

    response = client.get(
        "/api/v1/search",
        params={
            "q": "laptop",
            "limit": 51,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_mercado_libre_client_normalizes_products() -> None:
    """El cliente debe convertir la respuesta externa."""

    payload = {
        "results": [
            {
                "id": "MLM123",
                "title": "Laptop de prueba",
                "price": 10000,
                "original_price": 12000,
                "currency_id": "MXN",
                "permalink": "https://www.mercadolibre.com.mx/producto",
                "thumbnail": "https://http2.mlstatic.com/test.jpg",
                "condition": "new",
                "shipping": {
                    "free_shipping": True,
                },
                "seller": {
                    "nickname": "VENDEDOR_PRUEBA",
                },
            }
        ]
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json=payload,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as http_client:
        mercado_libre = MercadoLibreClient(
            http_client=http_client,
        )

        products = await mercado_libre.search_products(
            query="laptop",
            limit=10,
        )

    assert len(products) == 1
    assert products[0].id == "MLM123"
    assert products[0].precio == 10000
    assert products[0].envio_gratis is True
    assert "VENDEDOR_PRUEBA" in products[0].tienda


@pytest.mark.asyncio
async def test_service_uses_fallback_when_store_fails() -> None:
    """El servicio debe usar respaldo ante un error externo."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=403,
            json={"message": "forbidden"},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as http_client:
        mercado_libre = MercadoLibreClient(
            http_client=http_client,
        )

        service = ProductSearchService(
            mercado_libre=mercado_libre,
        )

        result = await service.search(
            query="laptop",
            limit=10,
        )

    assert result.fallback_used is True
    assert result.source == "simulated_fallback"
    assert result.total == 2
    assert result.warning is not None