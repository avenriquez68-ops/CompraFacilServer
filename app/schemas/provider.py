"""Esquemas comunes para proveedores de productos."""

from pydantic import BaseModel, Field

from app.schemas.product import Product


class ProviderSearchResult(BaseModel):
    """Resultado normalizado devuelto por una tienda."""

    store: str = Field(
        description="Nombre de la tienda consultada.",
    )

    products: list[Product] = Field(
        default_factory=list,
        description="Productos encontrados en la tienda.",
    )

    succeeded: bool = Field(
        default=True,
        description="Indica si la consulta terminó correctamente.",
    )

    warning: str | None = Field(
        default=None,
        description="Advertencia o detalle de un fallo controlado.",
    )