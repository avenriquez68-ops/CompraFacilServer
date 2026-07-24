"""Esquemas para consultar proveedores habilitados."""

from pydantic import BaseModel, Field

from app.schemas.provider_info import ProviderType


class ProviderStatus(BaseModel):
    """Información pública de un proveedor habilitado."""

    provider_id: str = Field(
        description="Identificador interno único del proveedor.",
    )

    store_name: str = Field(
        description="Nombre público de la tienda.",
    )

    provider_type: ProviderType = Field(
        description="Tipo de proveedor.",
    )

    country_code: str = Field(
        min_length=2,
        max_length=2,
        description="Código ISO de dos letras del país.",
    )

    supports_free_shipping: bool = Field(
        description="Indica si informa sobre envío gratis.",
    )

    supports_ratings: bool = Field(
        description="Indica si ofrece calificaciones o reseñas.",
    )

    is_demo: bool = Field(
        description="Indica si utiliza información demostrativa.",
    )

    enabled: bool = Field(
        default=True,
        description="Indica si el proveedor está habilitado.",
    )


class ProviderListResponse(BaseModel):
    """Lista de proveedores configurados en la aplicación."""

    total: int = Field(
        ge=0,
        description="Cantidad de proveedores habilitados.",
    )

    providers: list[ProviderStatus]