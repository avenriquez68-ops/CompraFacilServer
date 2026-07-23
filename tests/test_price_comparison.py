"""Pruebas del motor de comparación de precios."""

import pytest
from pydantic import ValidationError

from app.schemas.comparison import ComparisonFilters, PriceOrder
from app.schemas.product import Product
from app.services.price_comparison import PriceComparisonService


def create_product(
    product_id: str,
    price: float,
    free_shipping: bool,
) -> Product:
    """Crea un producto de prueba."""

    return Product(
        id=product_id,
        nombre=f"Producto {product_id}",
        precio=price,
        precio_original=None,
        moneda="MXN",
        url=f"https://example.com/{product_id}",
        imagen=None,
        condicion="new",
        envio_gratis=free_shipping,
        tienda="Tienda de prueba",
    )


def test_comparison_orders_products_by_lowest_price() -> None:
    """Los productos deben poder ordenarse del menor al mayor precio."""

    service = PriceComparisonService()

    products = [
        create_product("1", 900, False),
        create_product("2", 300, True),
        create_product("3", 600, False),
    ]

    filters = ComparisonFilters(
        price_order=PriceOrder.PRICE_ASC,
    )

    result, summary = service.compare(
        products=products,
        filters=filters,
        stores_consulted=["Tienda de prueba"],
        stores_succeeded=["Tienda de prueba"],
    )

    assert [product.precio for product in result] == [
        300,
        600,
        900,
    ]

    assert summary.lowest_price == 300
    assert summary.highest_price == 900
    assert summary.average_price == 600


def test_comparison_filters_price_and_shipping() -> None:
    """Los filtros deben combinar precio y envío gratis."""

    service = PriceComparisonService()

    products = [
        create_product("1", 200, True),
        create_product("2", 500, False),
        create_product("3", 800, True),
        create_product("4", 1200, True),
    ]

    filters = ComparisonFilters(
        minimum_price=300,
        maximum_price=1000,
        free_shipping_only=True,
    )

    result, summary = service.compare(
        products=products,
        filters=filters,
    )

    assert len(result) == 1
    assert result[0].id == "3"

    assert summary.products_before_filters == 4
    assert summary.products_after_filters == 1
    assert summary.lowest_price == 800
    assert summary.highest_price == 800


def test_comparison_rejects_invalid_price_range() -> None:
    """El precio mínimo no puede superar al precio máximo."""

    with pytest.raises(ValidationError):
        ComparisonFilters(
            minimum_price=1000,
            maximum_price=500,
        )


def test_comparison_handles_empty_results() -> None:
    """Una comparación vacía debe devolver estadísticas seguras."""

    service = PriceComparisonService()

    result, summary = service.compare(
        products=[],
        filters=ComparisonFilters(),
        stores_consulted=["Mercado Libre"],
        stores_failed=["Mercado Libre"],
    )

    assert result == []
    assert summary.products_before_filters == 0
    assert summary.products_after_filters == 0
    assert summary.lowest_price is None
    assert summary.highest_price is None
    assert summary.average_price is None