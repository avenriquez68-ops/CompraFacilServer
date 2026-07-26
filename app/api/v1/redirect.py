"""Endpoint para redirigir a productos de tiendas externas."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.api.dependencies import get_affiliate_link_service
from app.services.affiliate_link import AffiliateLinkService


router = APIRouter(
    prefix="/redirect",
    tags=["affiliate"],
)


@router.get(
    "",
    response_class=RedirectResponse,
    summary="Redirigir a un producto",
    description=(
        "Genera el enlace comercial correspondiente y redirige "
        "al usuario hacia la tienda."
    ),
)
def redirect_to_product(
    provider_id: Annotated[
        str,
        Query(
            min_length=1,
            max_length=50,
            description="Identificador interno del proveedor.",
            examples=["mercado_libre"],
        ),
    ],
    product_url: Annotated[
        str,
        Query(
            min_length=1,
            max_length=2048,
            description="URL original del producto.",
        ),
    ],
    service: Annotated[
        AffiliateLinkService,
        Depends(get_affiliate_link_service),
    ],
) -> RedirectResponse:
    """Genera el destino comercial y devuelve una redirección HTTP."""

    try:
        destination_url = service.build(
            provider_id=provider_id,
            product_url=product_url,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return RedirectResponse(
        url=destination_url,
        status_code=307,
    )