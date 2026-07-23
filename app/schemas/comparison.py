"""Esquemas utilizados por el motor de comparación de precios."""

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class PriceOrder(StrEnum):
    """Opciones disponibles para ordenar productos."""

    RELEVANCE = "relevance"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"


class ComparisonFilters(BaseModel):
    """Filtros que se aplican a los productos encontrados."""

    minimum_price: float | None = Field(
        default=None,
        ge=0,
        description="Precio mínimo permitido.",
    )

    maximum_price: float | None = Field(
        default=None,
        ge=0,
        description="Precio máximo permitido.",
    )

    free_shipping_only: bool = Field(
        default=False,
        description="Mostrar únicamente productos con envío gratis.",
    )

    price_order: PriceOrder = Field(
        default=PriceOrder.RELEVANCE,
        description="Orden en el que se mostrarán los productos.",
    )

    @model_validator(mode="after")
    def validate_price_range(self) -> "ComparisonFilters":
        """Comprueba que el precio mínimo no supere al máximo."""

        if (
            self.minimum_price is not None
            and self.maximum_price is not None
            and self.minimum_price > self.maximum_price
        ):
            raise ValueError(
                "minimum_price no puede ser mayor que maximum_price."
            )

        return self


class ComparisonSummary(BaseModel):
    """Resumen estadístico de una comparación."""

    stores_consulted: list[str] = Field(default_factory=list)
    stores_succeeded: list[str] = Field(default_factory=list)
    stores_failed: list[str] = Field(default_factory=list)

    products_before_filters: int = Field(default=0, ge=0)
    products_after_filters: int = Field(default=0, ge=0)

    lowest_price: float | None = Field(default=None, ge=0)
    highest_price: float | None = Field(default=None, ge=0)
    average_price: float | None = Field(default=None, ge=0)