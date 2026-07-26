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

def test_provider_registry_selects_all_when_ids_are_none() -> None:
    """El registro debe devolver todos los proveedores sin filtro."""

    mercado_libre_client = AsyncMock()

    test_settings = Settings(
        enable_demo_store=True,
    )

    registry = build_provider_registry(
        mercado_libre=mercado_libre_client,
        app_settings=test_settings,
    )

    providers = registry.select(
        provider_ids=None,
    )

    assert len(providers) == 2
    assert providers[0].info.provider_id == "mercado_libre"
    assert providers[1].info.provider_id == "demo_store"


def test_provider_registry_selects_requested_providers() -> None:
    """El registro debe devolver únicamente los proveedores solicitados."""

    mercado_libre_client = AsyncMock()

    test_settings = Settings(
        enable_demo_store=True,
    )

    registry = build_provider_registry(
        mercado_libre=mercado_libre_client,
        app_settings=test_settings,
    )

    providers = registry.select(
        provider_ids=[
            "demo_store",
        ],
    )

    assert len(providers) == 1
    assert providers[0].info.provider_id == "demo_store"


def test_provider_registry_preserves_requested_order() -> None:
    """El registro debe respetar el orden solicitado."""

    mercado_libre_client = AsyncMock()

    test_settings = Settings(
        enable_demo_store=True,
    )

    registry = build_provider_registry(
        mercado_libre=mercado_libre_client,
        app_settings=test_settings,
    )

    providers = registry.select(
        provider_ids=[
            "demo_store",
            "mercado_libre",
        ],
    )

    provider_ids = [
        provider.info.provider_id
        for provider in providers
    ]

    assert provider_ids == [
        "demo_store",
        "mercado_libre",
    ]


def test_provider_registry_ignores_duplicate_provider_ids() -> None:
    """El registro no debe devolver proveedores duplicados."""

    mercado_libre_client = AsyncMock()

    test_settings = Settings(
        enable_demo_store=True,
    )

    registry = build_provider_registry(
        mercado_libre=mercado_libre_client,
        app_settings=test_settings,
    )

    providers = registry.select(
        provider_ids=[
            "mercado_libre",
            "mercado_libre",
            "demo_store",
        ],
    )

    provider_ids = [
        provider.info.provider_id
        for provider in providers
    ]

    assert provider_ids == [
        "mercado_libre",
        "demo_store",
    ]


def test_provider_registry_reports_unknown_provider_ids() -> None:
    """El registro debe identificar proveedores inexistentes."""

    mercado_libre_client = AsyncMock()

    test_settings = Settings(
        enable_demo_store=True,
    )

    registry = build_provider_registry(
        mercado_libre=mercado_libre_client,
        app_settings=test_settings,
    )

    unknown_ids = registry.get_unknown_ids(
        provider_ids=[
            "mercado_libre",
            "amazon",
            "walmart",
        ],
    )

    assert unknown_ids == [
        "amazon",
        "walmart",
    ]