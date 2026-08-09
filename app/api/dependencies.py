"""Dependencias compartidas por los endpoints de la API."""

from app.affiliates.registry import (
    AffiliateLinkBuilderRegistry,
    build_affiliate_link_builder_registry,
)
from app.infrastructure.clients.mercado_libre import (
    MercadoLibreClient,
)
from app.providers.registry import (
    ProviderRegistry,
    build_provider_registry,
)
from app.services.affiliate_link import AffiliateLinkService
from app.services.product_search import ProductSearchService
from app.services.mercado_libre_token import (
    mercado_libre_token_service,
)

from app.repositories.affiliate_click import (
    AffiliateClickRepository,
    affiliate_click_repository,
)

from app.infrastructure.clients.mercado_libre_oauth import (
    MercadoLibreOAuthClient,
)
from app.repositories.mercado_libre_credential import (
    MercadoLibreCredentialRepository,
    mercado_libre_credential_repository,
)

def get_product_search_service() -> ProductSearchService:
    """Construye el servicio principal de búsqueda de productos."""

    registry = get_provider_registry()

    return ProductSearchService(
        registry=registry,
    )

def get_mercado_libre_client() -> MercadoLibreClient:
    """Construye el cliente con acceso a tokens persistentes."""

    return MercadoLibreClient(
        token_provider=mercado_libre_token_service,
    )

def get_provider_registry() -> ProviderRegistry:
    """Construye el registro central de proveedores."""

    return build_provider_registry(
        mercado_libre=get_mercado_libre_client(),
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

def get_affiliate_click_repository() -> AffiliateClickRepository:
    """Proporciona el repositorio de clics de afiliados."""

    return affiliate_click_repository

def get_mercado_libre_oauth_client(
) -> MercadoLibreOAuthClient:
    """Construye el cliente OAuth de Mercado Libre."""

    return MercadoLibreOAuthClient()


def get_mercado_libre_credential_repository(
) -> MercadoLibreCredentialRepository:
    """Proporciona el repositorio de credenciales."""

    return mercado_libre_credential_repository