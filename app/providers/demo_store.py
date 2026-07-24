"""Proveedor temporal utilizado para validar búsquedas multitienda."""

from app.providers.base import ProductProvider
from app.schemas.product import Product
from app.schemas.provider import ProviderSearchResult

from app.schemas.provider_info import (
    ProviderInfo,
    ProviderType,
)


DEMO_STORE_PRODUCTS: tuple[Product, ...] = (
    Product(
        id="demo-store-001",
        nombre="Laptop Acer Aspire 5",
        precio=12499.00,
        precio_original=13999.00,
        moneda="MXN",
        tienda="Tienda Demo",
        url="https://example.com/products/demo-store-001",
        imagen_url=None,
        condicion="new",
        envio_gratis=True,
        calificacion=4.6,
        numero_resenas=128,
    ),
    Product(
        id="demo-store-002",
        nombre="Laptop ASUS VivoBook 15",
        precio=14299.00,
        precio_original=None,
        moneda="MXN",
        tienda="Tienda Demo",
        url="https://example.com/products/demo-store-002",
        imagen_url=None,
        condicion="new",
        envio_gratis=False,
        calificacion=4.4,
        numero_resenas=76,
    ),
    Product(
        id="demo-store-003",
        nombre="Audífonos Bluetooth JBL",
        precio=1599.00,
        precio_original=1899.00,
        moneda="MXN",
        tienda="Tienda Demo",
        url="https://example.com/products/demo-store-003",
        imagen_url=None,
        condicion="new",
        envio_gratis=True,
        calificacion=4.7,
        numero_resenas=315,
    ),
)


class DemoStoreProvider(ProductProvider):
    """Proveedor temporal con un catálogo local controlado."""

    @property
    def store_name(self) -> str:
        """Devuelve el nombre público de la tienda."""

        return "Tienda Demo"

    @property
    def info(self) -> ProviderInfo:
        """Devuelve la información descriptiva del proveedor."""

        return ProviderInfo(
            provider_id="demo_store",
            display_name="Tienda Demo",
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
        """Busca productos dentro del catálogo de demostración."""

        normalized_query = query.strip().casefold()

        products = [
            product
            for product in DEMO_STORE_PRODUCTS
            if normalized_query in product.nombre.casefold()
            or normalized_query in product.tienda.casefold()
        ]

        return ProviderSearchResult(
            store=self.store_name,
            products=products[:limit],
            succeeded=True,
            warning=None,
        )