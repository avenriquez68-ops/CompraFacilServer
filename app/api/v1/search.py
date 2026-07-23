"""Endpoints relacionados con la búsqueda de productos."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.infrastructure.clients.mercado_libre import mercado_libre_client
from app.infrastructure.database.connection import get_database_session
from app.repositories.search_history import search_history_repository
from app.schemas.product import SearchResponse
from app.schemas.search_history import SearchHistoryItem
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
    session: Annotated[
        Session,
        Depends(get_database_session),
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
    """Devuelve productos y guarda la búsqueda."""

    service = ProductSearchService(
        mercado_libre=mercado_libre_client,
    )

    result = await service.search(
        query=q,
        limit=limit,
    )

    search_history_repository.create(
        session=session,
        search_result=result,
    )

    return result


@router.get(
    "/history",
    response_model=list[SearchHistoryItem],
    summary="Consultar historial",
)
def get_search_history(
    session: Annotated[
        Session,
        Depends(get_database_session),
    ],
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Cantidad máxima de búsquedas.",
        ),
    ] = 20,
) -> list[SearchHistoryItem]:
    """Devuelve las búsquedas más recientes."""

    history = search_history_repository.list_recent(
        session=session,
        limit=limit,
    )

    return [
        SearchHistoryItem.model_validate(item)
        for item in history
    ]