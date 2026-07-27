"""Endpoints para consultar clics de afiliados."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
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
) -> AffiliateClickStatsResponse:
    """Devuelve totales y clics recientes."""

    return AffiliateClickStatsResponse(
        total_clicks=repository.count_total(
            session=session,
        ),
        clicks_by_provider=repository.count_by_provider(
            session=session,
        ),
        recent_clicks=repository.list_recent(
            session=session,
            limit=limit,
        ),
    )