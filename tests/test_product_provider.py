"""Pruebas del contrato común de proveedores."""

import pytest

from app.providers.base import ProductProvider
from app.schemas.product import Product
from app.schemas.provider import ProviderSearchResult
from app.schemas.provider_info import ProviderInfo, ProviderType


class FakeProductProvider(ProductProvider):
    """Proveedor simulado utilizado en pruebas."""

    @property
    def store_name(self) -> str:
        """Devuelve el nombre de la tienda simulada."""

        return "Tienda simulada"

    @property
    def info(self) -> ProviderInfo:
        """Devuelve información descriptiva del proveedor falso."""

        return ProviderInfo(
            provider_id="fake_product_provider",
            display_name=self.store_name,
            provider_type=ProviderType.DEMO,
            country_code="MX",
            supports_free_shipping=True,
            supports_ratings=True,
            is_demo=True,
        )

    async def search(
        self,
        query: str,
        limit: int,
    ) -> ProviderSearchResult:
        """Devuelve productos simulados."""

        products = [
            Product(
                id="fake-1",
                nombre=f"{query} básico",
                precio=500,
                precio_original=None,
                moneda="MXN",
                url="https://example.com/fake-1",
                imagen=None,
                condicion="new",
                envio_gratis=True,
                tienda=self.store_name,
            ),
            Product(
                id="fake-2",
                nombre=f"{query} avanzado",
                precio=900,
                precio_original=None,
                moneda="MXN",
                url="https://example.com/fake-2",
                imagen=None,
                condicion="new",
                envio_gratis=False,
                tienda=self.store_name,
            ),
        ]

        return ProviderSearchResult(
            store=self.store_name,
            products=products[:limit],
            succeeded=True,
        )


@pytest.mark.asyncio
async def test_fake_provider_returns_normalized_products() -> None:
    """El proveedor debe devolver productos normalizados."""

    provider = FakeProductProvider()

    result = await provider.search(
        query="laptop",
        limit=2,
    )

    assert result.store == "Tienda simulada"
    assert result.succeeded is True
    assert result.warning is None
    assert len(result.products) == 2

    assert result.products[0].nombre == "laptop básico"
    assert result.products[0].tienda == "Tienda simulada"


@pytest.mark.asyncio
async def test_fake_provider_respects_limit() -> None:
    """El proveedor debe respetar el límite solicitado."""

    provider = FakeProductProvider()

    result = await provider.search(
        query="celular",
        limit=1,
    )

    assert len(result.products) == 1
    assert result.products[0].id == "fake-1"


def test_product_provider_cannot_be_created_directly() -> None:
    """El contrato abstracto no debe poder instanciarse."""

    with pytest.raises(TypeError):
        ProductProvider()