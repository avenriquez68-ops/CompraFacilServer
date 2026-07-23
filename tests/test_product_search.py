"""Pruebas del servicio principal de búsqueda."""

from unittest.mock import AsyncMock

import pytest

from app.infrastructure.clients.exceptions import ExternalStoreError
from app.schemas.product import Product
from app.services.product_search import ProductSearchService


def create_product() -> Product:
    """Crea un producto de Mercado Libre para pruebas."""

    return Product(
        id="MLM-TEST-SEARCH-1",
        nombre="Laptop multitienda",
        precio=12000,
        precio_original=None,
        moneda="MXN",
        tienda="Mercado Libre",
        url="https://example.com/MLM-TEST-SEARCH-1",
        imagen_url=None,
        condicion="new",
        envio_gratis=True,
        calificacion=None,
        numero_resenas=0,
    )


@pytest.mark.asyncio
async def test_product_search_uses_multi_provider_flow() -> None:
    """El servicio debe devolver los productos del proveedor."""

    mercado_libre_client = AsyncMock()

    mercado_libre_client.search_products.return_value = [
        create_product(),
    ]

    service = ProductSearchService(
        mercado_libre=mercado_libre_client,
    )

    result = await service.search(
        query="  laptop  ",
        limit=10,
    )

    assert result.query == "laptop"
    assert result.source == "multi_provider"
    assert result.fallback_used is False
    assert result.warning is None
    assert result.total == 3

    assert result.metadata is not None
    assert result.metadata.source == "multi_provider"
    assert result.metadata.fallback_used is False

    assert result.metadata.stores_consulted == [
    "Mercado Libre",
    "Tienda Demo",
]

    assert result.metadata.stores_succeeded == [
    "Mercado Libre",
    "Tienda Demo",
]

    assert result.metadata.stores_failed == []
    assert result.metadata.warnings == []

    assert result.products[0].nombre == "Laptop multitienda"

    mercado_libre_client.search_products.assert_awaited_once_with(
        query="laptop",
        limit=10,
    )


@pytest.mark.asyncio
async def test_product_search_continues_when_one_store_fails() -> None:
    """La búsqueda debe continuar cuando solo una tienda falla."""

    mercado_libre_client = AsyncMock()

    mercado_libre_client.search_products.side_effect = (
        ExternalStoreError(
            "Mercado Libre no está disponible."
        )
    )

    service = ProductSearchService(
        mercado_libre=mercado_libre_client,
    )

    result = await service.search(
        query="laptop",
        limit=10,
    )

    assert result.query == "laptop"
    assert result.source == "multi_provider"
    assert result.fallback_used is False
    assert result.warning is not None
    assert result.total == 2
    assert len(result.products) == 2

    assert result.metadata is not None
    assert result.metadata.source == "multi_provider"
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

    assert result.metadata.warnings

    assert (
        "Mercado Libre no está disponible"
        in result.warning
    )

    assert result.total == 2
    assert len(result.products) == 2