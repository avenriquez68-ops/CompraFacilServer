"""Pruebas para el registro central de proveedores."""

from unittest.mock import AsyncMock

from app.core.config import Settings
from app.providers.demo_store import DemoStoreProvider
from app.providers.mercado_libre import MercadoLibreProvider
from app.providers.registry import build_product_providers


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