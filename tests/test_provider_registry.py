"""Pruebas para el registro central de proveedores."""

from unittest.mock import AsyncMock

from app.providers.demo_store import DemoStoreProvider
from app.providers.mercado_libre import MercadoLibreProvider
from app.providers.registry import build_product_providers


def test_registry_builds_expected_providers() -> None:
    """El registro debe construir todos los proveedores configurados."""

    mercado_libre_client = AsyncMock()

    providers = build_product_providers(
        mercado_libre=mercado_libre_client,
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