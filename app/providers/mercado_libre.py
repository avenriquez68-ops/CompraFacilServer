"""Proveedor de productos de Mercado Libre."""

from app.infrastructure.clients.mercado_libre import (
    MercadoLibreClient,
)
from app.providers.base import ProductProvider
from app.schemas.provider import ProviderSearchResult


class MercadoLibreProvider(ProductProvider):
    """Adapta Mercado Libre al contrato común de proveedores."""

    def __init__(
        self,
        client: MercadoLibreClient,
    ) -> None:
        """Inicializa el proveedor con su cliente HTTP."""

        self.client = client

    @property
    def store_name(self) -> str:
        """Devuelve el nombre público de la tienda."""

        return "Mercado Libre"

    async def search(
        self,
        query: str,
        limit: int,
    ) -> ProviderSearchResult:
        """Busca productos en Mercado Libre."""

        products = await self.client.search_products(
            query=query,
            limit=limit,
        )

        return ProviderSearchResult(
            store=self.store_name,
            products=products,
            succeeded=True,
        )