"""Esquemas para consultar proveedores habilitados."""

from pydantic import BaseModel, Field


class ProviderStatus(BaseModel):
    """Información pública de un proveedor habilitado."""

    store_name: str = Field(
        description="Nombre público de la tienda.",
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