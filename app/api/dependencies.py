"""Dependencias compartidas por los endpoints de la API."""

from app.affiliates.registry import (
    AffiliateLinkBuilderRegistry,
    build_affiliate_link_builder_registry,
)
from app.infrastructure.clients.mercado_libre import (
    mercado_libre_client,
)
from app.providers.registry import (
    ProviderRegistry,
    build_provider_registry,
)
from app.services.affiliate_link import AffiliateLinkService
from app.services.product_search import ProductSearchService


def get_product_search_service() -> ProductSearchService:
    """Construye el servicio principal de búsqueda de productos."""

    registry = get_provider_registry()

    return ProductSearchService(
        registry=registry,
    )


def get_provider_registry() -> ProviderRegistry:
    """Construye el registro central de proveedores."""

    return build_provider_registry(
        mercado_libre=mercado_libre_client,
    )


def get_affiliate_link_builder_registry(
) -> AffiliateLinkBuilderRegistry:
    """Construye el registro de generadores de enlaces comerciales."""

    return build_affiliate_link_builder_registry()


def get_affiliate_link_service() -> AffiliateLinkService:
    """Construye el servicio de enlaces comerciales."""

    registry = get_affiliate_link_builder_registry()

    return AffiliateLinkService(
        registry=registry,
    )