"""Registro central de proveedores de productos."""

from app.core.config import Settings, settings
from app.infrastructure.clients.mercado_libre import MercadoLibreClient
from app.providers.base import ProductProvider
from app.providers.demo_store import DemoStoreProvider
from app.providers.mercado_libre import MercadoLibreProvider


def build_product_providers(
    mercado_libre: MercadoLibreClient,
    app_settings: Settings = settings,
) -> list[ProductProvider]:
    """Construye los proveedores habilitados por configuración."""

    providers: list[ProductProvider] = [
        MercadoLibreProvider(
            client=mercado_libre,
        ),
    ]

    if app_settings.enable_demo_store:
        providers.append(
            DemoStoreProvider()
        )

    return providers