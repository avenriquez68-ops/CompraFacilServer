"""Esquemas de datos relacionados con productos."""

from pydantic import BaseModel, Field, HttpUrl


class Product(BaseModel):
    """Representa un producto encontrado en una tienda."""

    id: str = Field(
        description="Identificador único del producto.",
        examples=["ml-001"],
    )
    nombre: str = Field(
        description="Nombre comercial del producto.",
        examples=["Laptop Lenovo IdeaPad 15"],
    )
    precio: float = Field(
        gt=0,
        description="Precio actual del producto.",
        examples=[15499.99],
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
    calificacion: float | None = Field(
        default=None,
        ge=0,
        le=5,
        description="Calificación promedio del producto.",
        examples=[4.7],
    )
    numero_resenas: int = Field(
        default=0,
        ge=0,
        description="Cantidad de reseñas publicadas.",
        examples=[253],
    )