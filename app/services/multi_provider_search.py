"""Servicio para consultar múltiples proveedores."""

import asyncio

from app.providers.base import ProductProvider
from app.schemas.multi_provider import MultiProviderSearchResult
from app.schemas.provider import ProviderSearchResult


class MultiProviderSearchService:
    """Consulta varias tiendas y combina sus resultados."""

    def __init__(
        self,
        providers: list[ProductProvider],
    ) -> None:
        """Inicializa el servicio con una lista de proveedores."""

        self.providers = providers

    async def search(
        self,
        query: str,
        limit_per_provider: int,
    ) -> MultiProviderSearchResult:
        """Ejecuta las búsquedas en todos los proveedores."""

        stores_consulted = [
            provider.store_name
            for provider in self.providers
        ]

        raw_results = await asyncio.gather(
            *[
                self._search_provider(
                    provider=provider,
                    query=query,
                    limit=limit_per_provider,
                )
                for provider in self.providers
            ]
        )

        combined_products = []
        stores_succeeded = []
        stores_failed = []
        warnings = []

        for result in raw_results:
            if result.succeeded:
                stores_succeeded.append(result.store)
                combined_products.extend(result.products)
            else:
                stores_failed.append(result.store)

            if result.warning:
                warnings.append(result.warning)

        return MultiProviderSearchResult(
            products=combined_products,
            stores_consulted=stores_consulted,
            stores_succeeded=stores_succeeded,
            stores_failed=stores_failed,
            warnings=warnings,
        )

    async def _search_provider(
        self,
        provider: ProductProvider,
        query: str,
        limit: int,
    ) -> ProviderSearchResult:
        """Ejecuta una tienda y convierte sus errores en fallos controlados."""

        try:
            return await provider.search(
                query=query,
                limit=limit,
            )

        except Exception as error:
            return ProviderSearchResult(
                store=provider.store_name,
                products=[],
                succeeded=False,
                warning=(
                    f"No fue posible consultar "
                    f"{provider.store_name}: {error}"
                ),
            )