"""Esquemas de datos relacionados con productos."""

from pydantic import BaseModel, Field, HttpUrl
from app.schemas.comparison import ComparisonSummary

class Product(BaseModel):
    """Representa un producto encontrado en una tienda."""

    id: str = Field(
        description="Identificador único del producto.",
        examples=["MLM123456789"],
    )
    nombre: str = Field(
        description="Nombre comercial del producto.",
        examples=["Laptop Lenovo IdeaPad 15"],
    )
    precio: float = Field(
        ge=0,
        description="Precio actual del producto.",
        examples=[15499.99],
    )
    precio_original: float | None = Field(
        default=None,
        ge=0,
        description="Precio anterior o de lista, cuando está disponible.",
    )
    moneda: str = Field(
        min_length=3,
        max_length=3,
        description="Código de la moneda.",
        examples=["MXN"],
    )
    tienda: str = Field(
        description="Tienda donde se vende el producto.",
        examples=["Mercado Libre"],
    )
    url: HttpUrl = Field(
        description="Dirección para consultar el producto en la tienda."
    )
    imagen_url: HttpUrl | None = Field(
        default=None,
        description="Imagen principal del producto.",
    )
    condicion: str | None = Field(
        default=None,
        description="Condición del producto, por ejemplo nuevo o usado.",
    )
    envio_gratis: bool = Field(
        default=False,
        description="Indica si el producto ofrece envío gratis.",
    )
    calificacion: float | None = Field(
        default=None,
        ge=0,
        le=5,
        description="Calificación promedio del producto.",
    )
    numero_resenas: int = Field(
        default=0,
        ge=0,
        description="Cantidad de reseñas publicadas.",
    )


class SearchResponse(BaseModel):
    """Respuesta completa de una búsqueda de productos."""

    query: str
    total: int
    source: str
    fallback_used: bool = False
    warning: str | None = None
    products: list[Product]
    comparison: ComparisonSummary | None = None