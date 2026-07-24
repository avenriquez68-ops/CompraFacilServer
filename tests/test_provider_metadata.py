"""Pruebas para la información descriptiva de proveedores."""

from app.infrastructure.clients.mercado_libre import MercadoLibreClient
from app.providers.demo_store import DemoStoreProvider
from app.providers.mercado_libre import MercadoLibreProvider
from app.schemas.provider_info import ProviderType


def test_mercado_libre_provider_info() -> None:
    """Mercado Libre debe declarar correctamente sus capacidades."""

    provider = MercadoLibreProvider(
        client=MercadoLibreClient(),
    )

    info = provider.info

    assert provider.store_name == "Mercado Libre"
    assert info.provider_id == "mercado_libre"
    assert info.display_name == "Mercado Libre"
    assert info.provider_type == ProviderType.MARKETPLACE
    assert info.country_code == "MX"
    assert info.supports_free_shipping is True
    assert info.supports_ratings is True
    assert info.is_demo is False


def test_demo_store_provider_info() -> None:
    """Tienda Demo debe identificarse como proveedor demostrativo."""

    provider = DemoStoreProvider()

    info = provider.info

    assert provider.store_name == "Tienda Demo"
    assert info.provider_id == "demo_store"
    assert info.display_name == "Tienda Demo"
    assert info.provider_type == ProviderType.DEMO
    assert info.country_code == "MX"
    assert info.supports_free_shipping is True
    assert info.supports_ratings is True
    assert info.is_demo is True