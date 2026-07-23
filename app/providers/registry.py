"""Registro central de proveedores de productos."""

from app.infrastructure.clients.mercado_libre import MercadoLibreClient
from app.providers.base import ProductProvider
from app.providers.demo_store import DemoStoreProvider
from app.providers.mercado_libre import MercadoLibreProvider


def build_product_providers(
    mercado_libre: MercadoLibreClient,
) -> list[ProductProvider]:
    """Construye la lista de proveedores disponibles."""

    return [
        MercadoLibreProvider(
            client=mercado_libre,
        ),
        DemoStoreProvider(),
    ]