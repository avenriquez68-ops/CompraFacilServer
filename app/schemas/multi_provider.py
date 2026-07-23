"""Esquemas para búsquedas en múltiples proveedores."""

from pydantic import BaseModel, Field

from app.schemas.product import Product


class MultiProviderSearchResult(BaseModel):
    """Resultado combinado de varias tiendas."""

    products: list[Product] = Field(
        default_factory=list,
        description="Productos combinados de todas las tiendas.",
    )

    stores_consulted: list[str] = Field(
        default_factory=list,
        description="Tiendas que se intentaron consultar.",
    )

    stores_succeeded: list[str] = Field(
        default_factory=list,
        description="Tiendas que respondieron correctamente.",
    )

    stores_failed: list[str] = Field(
        default_factory=list,
        description="Tiendas que no pudieron responder.",
    )

    warnings: list[str] = Field(
        default_factory=list,
        description="Advertencias generadas durante la búsqueda.",
    )