"""Pruebas del proveedor de Mercado Libre."""

from unittest.mock import AsyncMock

import pytest

from app.providers.mercado_libre import MercadoLibreProvider
from app.schemas.product import Product
from app.services.multi_provider_search import (
    MultiProviderSearchService,
)


def create_product() -> Product:
    """Crea un producto normalizado para las pruebas."""

    return Product(
        id="MLM-TEST-1",
        nombre="Laptop de prueba",
        precio=10000,
        precio_original=None,
        moneda="MXN",
        url="https://example.com/MLM-TEST-1",
        imagen=None,
        condicion="new",
        envio_gratis=True,
        tienda="Mercado Libre",
    )


@pytest.mark.asyncio
async def test_mercado_libre_provider_returns_products() -> None:
    """El proveedor debe devolver productos normalizados."""

    client = AsyncMock()

    client.search_products.return_value = [
        create_product(),
    ]

    provider = MercadoLibreProvider(
        client=client,
    )

    result = await provider.search(
        query="laptop",
        limit=10,
    )

    assert result.store == "Mercado Libre"
    assert result.succeeded is True
    assert result.warning is None
    assert len(result.products) == 1
    assert result.products[0].nombre == "Laptop de prueba"

    client.search_products.assert_awaited_once_with(
        query="laptop",
        limit=10,
    )


def test_mercado_libre_provider_store_name() -> None:
    """El proveedor debe identificar correctamente la tienda."""

    client = AsyncMock()

    provider = MercadoLibreProvider(
        client=client,
    )

    assert provider.store_name == "Mercado Libre"


@pytest.mark.asyncio
async def test_mercado_libre_provider_works_with_orchestrator() -> None:
    """Mercado Libre debe funcionar dentro del orquestador."""

    client = AsyncMock()

    client.search_products.return_value = [
        create_product(),
    ]

    provider = MercadoLibreProvider(
        client=client,
    )

    service = MultiProviderSearchService(
        providers=[provider],
    )

    result = await service.search(
        query="laptop",
        limit_per_provider=5,
    )

    assert len(result.products) == 1

    assert result.stores_consulted == [
        "Mercado Libre",
    ]

    assert result.stores_succeeded == [
        "Mercado Libre",
    ]

    assert result.stores_failed == []
    assert result.warnings == []