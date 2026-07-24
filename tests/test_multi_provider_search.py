"""Pruebas del servicio de búsqueda multitienda."""

from app.providers.base import ProductProvider
from app.schemas.product import Product
from app.schemas.provider import ProviderSearchResult
from app.services.multi_provider_search import (
    MultiProviderSearchService,
)

import pytest

from app.schemas.provider_info import ProviderInfo, ProviderType

class SuccessfulProvider(ProductProvider):
    """Proveedor simulado que responde correctamente."""

    def __init__(
        self,
        store_name: str,
        product_id: str,
        price: float,
    ) -> None:
        self._store_name = store_name
        self.product_id = product_id
        self.price = price

    @property
    def store_name(self) -> str:
        """Devuelve el nombre del proveedor."""

        return self._store_name

    @property
    def info(self) -> ProviderInfo:
        """Devuelve información descriptiva del proveedor simulado."""

        return ProviderInfo(
            provider_id=self.store_name.lower().replace(" ", "_"),
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
        """Devuelve un producto simulado."""

        products = [
            Product(
                id=self.product_id,
                nombre=f"{query} en {self.store_name}",
                precio=self.price,
                precio_original=None,
                moneda="MXN",
                url=f"https://example.com/{self.product_id}",
                imagen=None,
                condicion="new",
                envio_gratis=True,
                tienda=self.store_name,
            )
        ]

        return ProviderSearchResult(
            store=self.store_name,
            products=products[:limit],
            succeeded=True,
        )


class FailingProvider(ProductProvider):
    """Proveedor simulado que genera un error."""
    @property
    def info(self) -> ProviderInfo:
        """Devuelve información descriptiva del proveedor fallido."""

        return ProviderInfo(
            provider_id="failing_provider",
            display_name=self.store_name,
            provider_type=ProviderType.DEMO,
            country_code="MX",
            supports_free_shipping=False,
            supports_ratings=False,
            is_demo=True,
        )

    @property
    def store_name(self) -> str:
        """Devuelve el nombre del proveedor."""

        return "Tienda con error"

    async def search(
        self,
        query: str,
        limit: int,
    ) -> ProviderSearchResult:
        """Simula una falla externa."""

        raise RuntimeError("Servicio no disponible")


@pytest.mark.asyncio
async def test_multi_provider_combines_products() -> None:
    """El servicio debe combinar productos de varias tiendas."""

    service = MultiProviderSearchService(
        providers=[
            SuccessfulProvider(
                store_name="Tienda Uno",
                product_id="one-1",
                price=500,
            ),
            SuccessfulProvider(
                store_name="Tienda Dos",
                product_id="two-1",
                price=700,
            ),
        ]
    )

    result = await service.search(
        query="laptop",
        limit_per_provider=10,
    )

    assert len(result.products) == 2

    assert result.stores_consulted == [
        "Tienda Uno",
        "Tienda Dos",
    ]

    assert result.stores_succeeded == [
        "Tienda Uno",
        "Tienda Dos",
    ]

    assert result.stores_failed == []
    assert result.warnings == []


@pytest.mark.asyncio
async def test_multi_provider_continues_when_one_store_fails() -> None:
    """Una tienda fallida no debe detener toda la búsqueda."""

    service = MultiProviderSearchService(
        providers=[
            SuccessfulProvider(
                store_name="Tienda Correcta",
                product_id="ok-1",
                price=800,
            ),
            FailingProvider(),
        ]
    )

    result = await service.search(
        query="celular",
        limit_per_provider=10,
    )

    assert len(result.products) == 1
    assert result.products[0].id == "ok-1"

    assert result.stores_consulted == [
        "Tienda Correcta",
        "Tienda con error",
    ]

    assert result.stores_succeeded == [
        "Tienda Correcta",
    ]

    assert result.stores_failed == [
        "Tienda con error",
    ]

    assert len(result.warnings) == 1

    assert (
        "No fue posible consultar Tienda con error"
        in result.warnings[0]
    )


@pytest.mark.asyncio
async def test_multi_provider_handles_empty_provider_list() -> None:
    """El servicio debe aceptar una lista vacía de proveedores."""

    service = MultiProviderSearchService(
        providers=[]
    )

    result = await service.search(
        query="audífonos",
        limit_per_provider=10,
    )

    assert result.products == []
    assert result.stores_consulted == []
    assert result.stores_succeeded == []
    assert result.stores_failed == []
    assert result.warnings == []