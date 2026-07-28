"""Endpoints para consultar clics de afiliados."""

from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_affiliate_click_repository
from app.infrastructure.database.connection import get_database_session
from app.repositories.affiliate_click import AffiliateClickRepository
from app.schemas.affiliate_click import AffiliateClickStatsResponse


router = APIRouter(
    prefix="/affiliate-clicks",
    tags=["affiliate"],
)


@router.get(
    "/stats",
    response_model=AffiliateClickStatsResponse,
    summary="Consultar estadísticas de clics",
)
def get_affiliate_click_stats(
    session: Annotated[
        Session,
        Depends(get_database_session),
    ],
    repository: Annotated[
        AffiliateClickRepository,
        Depends(get_affiliate_click_repository),
    ],
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Cantidad máxima de clics recientes.",
        ),
    ] = 20,
    provider_id: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=50,
            description="Proveedor que se desea consultar.",
        ),
    ] = None,
    date_from: Annotated[
        datetime | None,
        Query(
            description="Fecha inicial en formato ISO 8601.",
        ),
    ] = None,
    date_to: Annotated[
        datetime | None,
        Query(
            description="Fecha final en formato ISO 8601.",
        ),
    ] = None,
) -> AffiliateClickStatsResponse:
    """Devuelve totales y clics recientes."""

    if (
        date_from is not None
        and date_to is not None
        and date_from > date_to
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "date_from no puede ser posterior a date_to"
            ),
        )

    total_clicks = repository.count_total(
        session=session,
        provider_id=provider_id,
        date_from=date_from,
        date_to=date_to,
    )

    if provider_id is None:
        clicks_by_provider = repository.count_by_provider(
            session=session,
            date_from=date_from,
            date_to=date_to,
        )
    else:
        clicks_by_provider = {
            provider_id: total_clicks,
        }

    recent_clicks = repository.list_recent(
        session=session,
        limit=limit,
        provider_id=provider_id,
        date_from=date_from,
        date_to=date_to,
    )

    return AffiliateClickStatsResponse(
        total_clicks=total_clicks,
        clicks_by_provider=clicks_by_provider,
        recent_clicks=recent_clicks,
    )