"""Endpoints relacionados con la búsqueda de productos."""

from typing import Annotated

from fastapi import APIRouter, Query

from app.schemas.product import Product
from app.services.product_search import product_search_service

router = APIRouter(
    prefix="/search",
    tags=["Búsqueda"],
)


@router.get(
    "",
    response_model=list[Product],
    summary="Buscar productos",
    description=(
        "Busca productos simulados por nombre o por tienda. "
        "La búsqueda no distingue mayúsculas y minúsculas."
    ),
)
async def search_products(
    q: Annotated[
        str,
        Query(
            min_length=2,
            max_length=100,
            description="Nombre del producto que se desea buscar.",
            examples=["laptop"],
        ),
    ],
) -> list[Product]:
    """Devuelve los productos que coinciden con el texto buscado."""

    return product_search_service.search(q)