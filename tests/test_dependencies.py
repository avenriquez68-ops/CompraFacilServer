"""Pruebas para las dependencias compartidas de la API."""

from app.affiliates.registry import AffiliateLinkBuilderRegistry
from app.api.dependencies import (
    get_affiliate_click_repository,
    get_affiliate_link_builder_registry,
    get_affiliate_link_service,
)
from app.services.affiliate_link import AffiliateLinkService
from app.repositories.affiliate_click import AffiliateClickRepository


def test_get_affiliate_link_builder_registry() -> None:
    """Debe construir el registro de generadores comerciales."""

    registry = get_affiliate_link_builder_registry()

    assert isinstance(
        registry,
        AffiliateLinkBuilderRegistry,
    )
    assert registry.exists("mercado_libre") is True
    assert registry.exists("demo_store") is True


def test_get_affiliate_link_service() -> None:
    """Debe construir el servicio de enlaces comerciales."""

    service = get_affiliate_link_service()

    assert isinstance(
        service,
        AffiliateLinkService,
    )


def test_affiliate_link_service_dependency_builds_url() -> None:
    """El servicio construido debe generar una URL válida."""

    service = get_affiliate_link_service()

    product_url = (
        "https://www.mercadolibre.com.mx/producto/123"
    )

    result = service.build(
        provider_id="mercado_libre",
        product_url=product_url,
    )

    assert result == product_url


def test_affiliate_registry_dependency_returns_new_instance() -> None:
    """Cada llamada debe construir un registro independiente."""

    first_registry = get_affiliate_link_builder_registry()
    second_registry = get_affiliate_link_builder_registry()

    assert first_registry is not second_registry

def test_get_affiliate_click_repository() -> None:
    """Debe proporcionar el repositorio de clics."""

    repository = get_affiliate_click_repository()

    assert isinstance(
        repository,
        AffiliateClickRepository,
    )