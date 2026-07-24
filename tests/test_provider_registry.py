"""Pruebas para el registro central de proveedores."""

from unittest.mock import AsyncMock

from app.core.config import Settings
from app.providers.demo_store import DemoStoreProvider
from app.providers.mercado_libre import MercadoLibreProvider
from app.providers.registry import (
    ProviderRegistry,
    build_product_providers,
    build_provider_registry,
)


def test_registry_includes_demo_store_when_enabled() -> None:
    """El registro debe incluir Tienda Demo cuando está habilitada."""

    mercado_libre_client = AsyncMock()

    test_settings = Settings(
        enable_demo_store=True,
    )

    providers = build_product_providers(
        mercado_libre=mercado_libre_client,
        app_settings=test_settings,
    )

    assert len(providers) == 2
    assert isinstance(
        providers[0],
        MercadoLibreProvider,
    )
    assert isinstance(
        providers[1],
        DemoStoreProvider,
    )


def test_registry_excludes_demo_store_when_disabled() -> None:
    """El registro no debe incluir Tienda Demo cuando está deshabilitada."""

    mercado_libre_client = AsyncMock()

    test_settings = Settings(
        enable_demo_store=False,
    )

    providers = build_product_providers(
        mercado_libre=mercado_libre_client,
        app_settings=test_settings,
    )

    assert len(providers) == 1
    assert isinstance(
        providers[0],
        MercadoLibreProvider,
    )

    assert not any(
        isinstance(provider, DemoStoreProvider)
        for provider in providers
    )

def test_provider_registry_counts_registered_providers() -> None:
    """El registro debe informar cuántos proveedores contiene."""

    mercado_libre_client = AsyncMock()

    test_settings = Settings(
        enable_demo_store=True,
    )

    registry = build_provider_registry(
        mercado_libre=mercado_libre_client,
        app_settings=test_settings,
    )

    assert registry.count() == 2


def test_provider_registry_finds_existing_provider() -> None:
    """El registro debe encontrar proveedores por identificador."""

    mercado_libre_client = AsyncMock()

    test_settings = Settings(
        enable_demo_store=True,
    )

    registry = build_provider_registry(
        mercado_libre=mercado_libre_client,
        app_settings=test_settings,
    )

    provider = registry.get("mercado_libre")

    assert provider is not None
    assert provider.info.provider_id == "mercado_libre"


def test_provider_registry_returns_none_for_unknown_provider() -> None:
    """El registro debe devolver None para un identificador desconocido."""

    registry = ProviderRegistry(
        providers=[],
    )

    provider = registry.get("unknown_provider")

    assert provider is None


def test_provider_registry_reports_provider_existence() -> None:
    """El registro debe indicar si un proveedor existe."""

    mercado_libre_client = AsyncMock()

    test_settings = Settings(
        enable_demo_store=True,
    )

    registry = build_provider_registry(
        mercado_libre=mercado_libre_client,
        app_settings=test_settings,
    )

    assert registry.exists("mercado_libre") is True
    assert registry.exists("demo_store") is True
    assert registry.exists("unknown_provider") is False


def test_provider_registry_returns_copy_of_provider_list() -> None:
    """Modificar la lista pública no debe alterar el registro interno."""

    mercado_libre_client = AsyncMock()

    test_settings = Settings(
        enable_demo_store=False,
    )

    registry = build_provider_registry(
        mercado_libre=mercado_libre_client,
        app_settings=test_settings,
    )

    providers = registry.providers
    providers.clear()

    assert providers == []
    assert registry.count() == 1