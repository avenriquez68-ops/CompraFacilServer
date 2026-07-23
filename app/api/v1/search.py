"""Endpoints relacionados con la búsqueda de productos."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.infrastructure.clients.mercado_libre import mercado_libre_client
from app.infrastructure.database.connection import get_database_session
from app.repositories.search_history import search_history_repository
from app.schemas.product import SearchResponse
from app.schemas.search_history import SearchHistoryItem
from app.services.product_search import ProductSearchService

from app.schemas.comparison import ComparisonFilters, PriceOrder
from app.services.price_comparison import price_comparison_service

router = APIRouter(
    prefix="/search",
    tags=["Búsqueda"],
)


@router.get(
    "",
    response_model=SearchResponse,
    summary="Buscar productos",
    description=(
        "Busca y compara productos en múltiples tiendas. "
        "Si una tienda falla, continúa con las demás disponibles."
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

    minimum_price: Annotated[
        float | None,
        Query(
            ge=0,
            description="Precio mínimo permitido.",
        ),
    ] = None,
    maximum_price: Annotated[
        float | None,
        Query(
            ge=0,
            description="Precio máximo permitido.",
        ),
    ] = None,
    free_shipping_only: Annotated[
        bool,
        Query(
            description="Mostrar únicamente productos con envío gratis.",
        ),
    ] = False,
    price_order: Annotated[
        PriceOrder,
        Query(
            description="Orden de los productos.",
        ),
    ] = PriceOrder.RELEVANCE,


) -> SearchResponse:
    """Devuelve productos y guarda la búsqueda."""

    if (
        minimum_price is not None
        and maximum_price is not None
        and minimum_price > maximum_price
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "minimum_price no puede ser mayor "
                "que maximum_price."
            ),
        )

    service = ProductSearchService(
        mercado_libre=mercado_libre_client,
    )

    result = await service.search(
        query=q,
        limit=limit,
    )

    filters = ComparisonFilters(
        minimum_price=minimum_price,
        maximum_price=maximum_price,
        free_shipping_only=free_shipping_only,
        price_order=price_order,
    )

    compared_products, comparison_summary = (
    price_comparison_service.compare(
        products=result.products,
        filters=filters,
        stores_consulted=(
            result.metadata.stores_consulted
            if result.metadata is not None
            else []
        ),
        stores_succeeded=(
            result.metadata.stores_succeeded
            if result.metadata is not None
            else []
        ),
        stores_failed=(
            result.metadata.stores_failed
            if result.metadata is not None
            else []
        ),
    )
)

    result.products = compared_products
    result.total = len(compared_products)
    result.comparison = comparison_summary

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