"""Metadatos técnicos de una búsqueda de productos."""

from pydantic import BaseModel, Field


class SearchMetadata(BaseModel):
    """Información técnica sobre la ejecución de una búsqueda."""

    source: str = Field(
        description="Origen general de los resultados.",
        examples=["multi_provider"],
    )

    fallback_used: bool = Field(
        default=False,
        description="Indica si se utilizaron productos de respaldo.",
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