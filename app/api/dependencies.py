"""Dependencias compartidas por los endpoints de la API."""

from app.infrastructure.clients.mercado_libre import (
    mercado_libre_client,
)
from app.providers.registry import (
    ProviderRegistry,
    build_provider_registry,
)

from app.services.product_search import ProductSearchService


def get_product_search_service() -> ProductSearchService:
    """Construye el servicio principal de búsqueda de productos."""

    return ProductSearchService(
        mercado_libre=mercado_libre_client,
    )

def get_provider_registry() -> ProviderRegistry:
    """Construye el registro central de proveedores."""

    return build_provider_registry(
        mercado_libre=mercado_libre_client,
    )