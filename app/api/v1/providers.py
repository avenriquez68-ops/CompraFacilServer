"""Endpoints relacionados con proveedores de productos."""

from fastapi import APIRouter

from app.infrastructure.clients.mercado_libre import (
    mercado_libre_client,
)
from app.providers.registry import build_product_providers
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
def get_enabled_providers() -> ProviderListResponse:
    """Devuelve los proveedores habilitados por configuración."""

    providers = build_product_providers(
        mercado_libre=mercado_libre_client,
    )

    provider_statuses = [
        ProviderStatus(
            store_name=provider.store_name,
            enabled=True,
        )
        for provider in providers
    ]

    return ProviderListResponse(
        total=len(provider_statuses),
        providers=provider_statuses,
    )