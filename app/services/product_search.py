"""Servicio encargado de coordinar la búsqueda de productos."""

from app.infrastructure.clients.exceptions import ExternalStoreError
from app.infrastructure.clients.mercado_libre import MercadoLibreClient
from app.schemas.product import Product, SearchResponse


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
    """Coordina búsquedas en tiendas y el respaldo simulado."""

    def __init__(
        self,
        mercado_libre: MercadoLibreClient,
    ) -> None:
        self._mercado_libre = mercado_libre

    async def search(
        self,
        query: str,
        limit: int,
    ) -> SearchResponse:
        """Busca productos reales y usa respaldo si ocurre un error."""

        normalized_query = query.strip()

        try:
            products = await self._mercado_libre.search_products(
                query=normalized_query,
                limit=limit,
            )

            return SearchResponse(
                query=normalized_query,
                total=len(products),
                source="mercado_libre",
                fallback_used=False,
                products=products,
            )

        except ExternalStoreError as exc:
            fallback_products = self._search_fallback(
                query=normalized_query,
                limit=limit,
            )

            return SearchResponse(
                query=normalized_query,
                total=len(fallback_products),
                source="simulated_fallback",
                fallback_used=True,
                warning=str(exc),
                products=fallback_products,
            )

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