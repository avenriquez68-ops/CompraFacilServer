"""Información descriptiva de los proveedores de productos."""

from enum import StrEnum

from pydantic import BaseModel, Field


class ProviderType(StrEnum):
    """Tipos de proveedores admitidos por la aplicación."""

    MARKETPLACE = "marketplace"
    RETAILER = "retailer"
    DEMO = "demo"


class ProviderInfo(BaseModel):
    """Descripción pública y capacidades de un proveedor."""

    provider_id: str = Field(
        min_length=2,
        max_length=50,
        description="Identificador interno único del proveedor.",
    )

    display_name: str = Field(
        min_length=2,
        max_length=100,
        description="Nombre público mostrado al usuario.",
    )

    provider_type: ProviderType = Field(
        description="Tipo de tienda o proveedor.",
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
        default=False,
        description="Indica si utiliza información demostrativa.",
    )