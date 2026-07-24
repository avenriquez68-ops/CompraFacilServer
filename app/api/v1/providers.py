"""Endpoints relacionados con proveedores de productos."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_provider_registry
from app.providers.registry import ProviderRegistry
from app.schemas.provider_status import (
    ProviderListResponse,
    ProviderStatus,
)

router = APIRouter(
    prefix="/providers",
    tags=["Proveedores"],
)


@router.get(
    "",
    response_model=ProviderListResponse,
    summary="Consultar proveedores habilitados",
    description=(
        "Devuelve las tiendas que participan actualmente "
        "en la búsqueda de productos."
    ),
)
def get_enabled_providers(
    registry: ProviderRegistry = Depends(
        get_provider_registry
    ),
) -> ProviderListResponse:

    """Devuelve los proveedores habilitados por configuración."""

    
    provider_statuses: list[ProviderStatus] = []

    for provider in registry.providers:
        info = provider.info

        provider_statuses.append(
            ProviderStatus(
                provider_id=info.provider_id,
                store_name=info.display_name,
                provider_type=info.provider_type,
                country_code=info.country_code,
                supports_free_shipping=(
                    info.supports_free_shipping
                ),
                supports_ratings=info.supports_ratings,
                is_demo=info.is_demo,
                enabled=True,
            )
        )

    return ProviderListResponse(
        total=len(provider_statuses),
        providers=provider_statuses,
    )


    return ProviderListResponse(
        total=len(provider_statuses),
        providers=provider_statuses,
    )