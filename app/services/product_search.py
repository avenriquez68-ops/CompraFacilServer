"""Servicio encargado de coordinar la búsqueda de productos."""

from app.infrastructure.clients.mercado_libre import (
    MercadoLibreClient,
)
from app.providers.mercado_libre import MercadoLibreProvider
from app.schemas.product import Product, SearchResponse
from app.schemas.search_metadata import SearchMetadata
from app.services.multi_provider_search import (
    MultiProviderSearchService,
)


FALLBACK_PRODUCTS: tuple[Product, ...] = (
    Product(
        id="demo-ml-001",
        nombre="Laptop Lenovo IdeaPad 15",
        precio=15499.99,
        precio_original=16999.99,
        moneda="MXN",
        tienda="Mercado Libre · Datos de demostración",
        url="https://www.mercadolibre.com.mx/",
        imagen_url=None,
        condicion="new",
        envio_gratis=True,
        calificacion=4.7,
        numero_resenas=253,
    ),
    Product(
        id="demo-ml-002",
        nombre="Laptop HP 14 pulgadas",
        precio=13299.00,
        precio_original=None,
        moneda="MXN",
        tienda="Mercado Libre · Datos de demostración",
        url="https://www.mercadolibre.com.mx/",
        imagen_url=None,
        condicion="new",
        envio_gratis=True,
        calificacion=4.5,
        numero_resenas=187,
    ),
    Product(
        id="demo-ml-003",
        nombre="Audífonos inalámbricos Sony",
        precio=1899.00,
        precio_original=2199.00,
        moneda="MXN",
        tienda="Mercado Libre · Datos de demostración",
        url="https://www.mercadolibre.com.mx/",
        imagen_url=None,
        condicion="new",
        envio_gratis=False,
        calificacion=4.8,
        numero_resenas=641,
    ),
)


class ProductSearchService:
    """Coordina búsquedas multitienda y el respaldo simulado."""

    def __init__(
        self,
        mercado_libre: MercadoLibreClient,
    ) -> None:
        """Configura los proveedores disponibles."""

        mercado_libre_provider = MercadoLibreProvider(
            client=mercado_libre,
        )

        self._multi_provider_service = MultiProviderSearchService(
            providers=[
                mercado_libre_provider,
            ],
        )

    async def search(
        self,
        query: str,
        limit: int,
    ) -> SearchResponse:
        """Busca productos y usa respaldo si todas las tiendas fallan."""

        normalized_query = query.strip()

        multi_provider_result = (
            await self._multi_provider_service.search(
                query=normalized_query,
                limit_per_provider=limit,
            )
        )

        warning_text = self._build_warning(
            multi_provider_result.warnings
        )

        if multi_provider_result.stores_succeeded:
            metadata = SearchMetadata(
                source="multi_provider",
                fallback_used=False,
                stores_consulted=(
                    multi_provider_result.stores_consulted
                ),
                stores_succeeded=(
                    multi_provider_result.stores_succeeded
                ),
                stores_failed=(
                    multi_provider_result.stores_failed
                ),
                warnings=multi_provider_result.warnings,
            )

            return SearchResponse(
                query=normalized_query,
                total=len(multi_provider_result.products),
                source="mercado_libre",
                fallback_used=False,
                warning=warning_text,
                products=multi_provider_result.products,
                metadata=metadata,
            )

        fallback_products = self._search_fallback(
            query=normalized_query,
            limit=limit,
        )

        metadata = SearchMetadata(
            source="simulated_fallback",
            fallback_used=True,
            stores_consulted=(
                multi_provider_result.stores_consulted
            ),
            stores_succeeded=(
                multi_provider_result.stores_succeeded
            ),
            stores_failed=multi_provider_result.stores_failed,
            warnings=multi_provider_result.warnings,
        )

        return SearchResponse(
            query=normalized_query,
            total=len(fallback_products),
            source="simulated_fallback",
            fallback_used=True,
            warning=warning_text,
            products=fallback_products,
            metadata=metadata,
        )

  
    @staticmethod
    def _build_warning(
        warnings: list[str],
    ) -> str | None:
        """Combina las advertencias generadas por los proveedores."""

        if not warnings:
            return None

        return " ".join(warnings)

    @staticmethod
    def _search_fallback(
        query: str,
        limit: int,
    ) -> list[Product]:
        """Busca dentro del catálogo de respaldo."""

        normalized_query = query.casefold()

        products = [
            product
            for product in FALLBACK_PRODUCTS
            if normalized_query in product.nombre.casefold()
            or normalized_query in product.tienda.casefold()
        ]

        return products[:limit]