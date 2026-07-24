"""Dependencias compartidas por los endpoints de la API."""

from app.infrastructure.clients.mercado_libre import (
    mercado_libre_client,
)
from app.services.product_search import ProductSearchService


def get_product_search_service() -> ProductSearchService:
    """Construye el servicio principal de búsqueda de productos."""

    return ProductSearchService(
        mercado_libre=mercado_libre_client,
    )