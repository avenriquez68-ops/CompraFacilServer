"""Endpoints relacionados con la búsqueda de productos."""

from typing import Annotated

from fastapi import APIRouter, Query

from app.infrastructure.clients.mercado_libre import mercado_libre_client
from app.schemas.product import SearchResponse
from app.services.product_search import ProductSearchService

router = APIRouter(
    prefix="/search",
    tags=["Búsqueda"],
)


@router.get(
    "",
    response_model=SearchResponse,
    summary="Buscar productos",
    description=(
        "Busca productos en Mercado Libre México. "
        "Si la tienda no está disponible, utiliza datos de respaldo."
    ),
)
async def search_products(
    q: Annotated[
        str,
        Query(
            min_length=2,
            max_length=100,
            description="Producto que se desea buscar.",
            examples=["laptop"],
        ),
    ],
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=50,
            description="Cantidad máxima de productos.",
        ),
    ] = 20,
) -> SearchResponse:
    """Devuelve productos reales o datos de respaldo."""

    service = ProductSearchService(
        mercado_libre=mercado_libre_client,
    )

    return await service.search(
        query=q,
        limit=limit,
    )