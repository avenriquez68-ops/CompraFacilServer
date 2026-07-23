"""Pruebas para el proveedor de demostración."""

import pytest

from app.providers.demo_store import DemoStoreProvider


@pytest.mark.asyncio
async def test_demo_store_returns_matching_products() -> None:
    """Debe devolver los productos que coincidan con la consulta."""

    provider = DemoStoreProvider()

    result = await provider.search(
        query="laptop",
        limit=10,
    )

    assert result.store == "Tienda Demo"
    assert result.succeeded is True
    assert result.warning is None
    assert len(result.products) == 2

    assert all(
        "laptop" in product.nombre.casefold()
        for product in result.products
    )


@pytest.mark.asyncio
async def test_demo_store_respects_limit() -> None:
    """Debe respetar el límite solicitado."""

    provider = DemoStoreProvider()

    result = await provider.search(
        query="laptop",
        limit=1,
    )

    assert len(result.products) == 1


@pytest.mark.asyncio
async def test_demo_store_returns_empty_list_without_error() -> None:
    """Una búsqueda sin coincidencias no debe considerarse un fallo."""

    provider = DemoStoreProvider()

    result = await provider.search(
        query="producto inexistente",
        limit=10,
    )

    assert result.succeeded is True
    assert result.warning is None
    assert result.products == []