"""Pruebas del endpoint de búsqueda."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.infrastructure.clients.mercado_libre import MercadoLibreClient
from app.main import app
from app.services.product_search import ProductSearchService
from app.api.dependencies import get_product_search_service
from app.schemas.product import Product, SearchResponse

class FakeProductSearchService:
    """Servicio de búsqueda simulado para probar el endpoint."""

    async def search(
        self,
        query: str,
        limit: int,
    ) -> SearchResponse:
        """Devuelve una respuesta controlada sin consultar tiendas reales."""

        products = [
            Product(
                id="fake-001",
                nombre="Laptop de prueba",
                precio=9999,
                precio_original=None,
                moneda="MXN",
                tienda="Tienda Simulada",
                url="https://example.com/fake-001",
                imagen_url=None,
                condicion="new",
                envio_gratis=True,
                calificacion=4.8,
                numero_resenas=25,
            ),
        ]

        return SearchResponse(
            query=query,
            total=len(products),
            source="test_provider",
            fallback_used=False,
            warning=None,
            products=products[:limit],
            metadata=None,
        )

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
async def test_service_continues_when_one_store_fails() -> None:
    """El servicio debe continuar si al menos una tienda responde."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=403,
            json={"message": "forbidden"},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport
    ) as http_client:
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

    assert result.fallback_used is False
    assert result.source == "multi_provider"
    assert result.total == 2
    assert len(result.products) == 2
    assert result.warning is not None

    assert result.metadata is not None
    assert result.metadata.fallback_used is False

    assert result.metadata.stores_consulted == [
        "Mercado Libre",
        "Tienda Demo",
    ]

    assert result.metadata.stores_succeeded == [
        "Tienda Demo",
    ]

    assert result.metadata.stores_failed == [
        "Mercado Libre",
    ]

    assert (
        "Mercado Libre rechazó la consulta"
        in result.warning
    )

def test_search_rejects_invalid_price_range() -> None:
    """El endpoint debe rechazar un rango de precios inválido."""

    response = client.get(
        "/api/v1/search",
        params={
            "q": "laptop",
            "minimum_price": 20000,
            "maximum_price": 5000,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"] == (
        "minimum_price no puede ser mayor "
        "que maximum_price."
    )

def test_search_rejects_negative_minimum_price() -> None:
    """FastAPI debe rechazar precios mínimos negativos."""

    response = client.get(
        "/api/v1/search",
        params={
            "q": "laptop",
            "minimum_price": -1,
        },
    )

    assert response.status_code == 422

def test_search_rejects_invalid_price_order() -> None:
    """El endpoint debe rechazar un orden no permitido."""

    response = client.get(
        "/api/v1/search",
        params={
            "q": "laptop",
            "price_order": "incorrect_order",
        },
    )

    assert response.status_code == 422

def test_search_endpoint_uses_dependency_override() -> None:
    """El endpoint debe permitir sustituir el servicio de búsqueda."""

    def override_product_search_service() -> FakeProductSearchService:
        return FakeProductSearchService()

    app.dependency_overrides[
        get_product_search_service
    ] = override_product_search_service

    try:
        response = client.get(
            "/api/v1/search",
            params={
                "q": "laptop",
                "limit": 10,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "laptop"
    assert data["total"] == 1
    assert data["source"] == "test_provider"
    assert data["fallback_used"] is False

    assert len(data["products"]) == 1
    assert data["products"][0]["id"] == "fake-001"
    assert data["products"][0]["tienda"] == "Tienda Simulada"