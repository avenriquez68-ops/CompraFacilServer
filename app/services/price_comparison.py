"""Reglas para filtrar, ordenar y resumir productos."""

from app.schemas.comparison import (
    ComparisonFilters,
    ComparisonSummary,
    PriceOrder,
)
from app.schemas.product import Product


class PriceComparisonService:
    """Aplica reglas de comparación a productos normalizados."""

    def compare(
        self,
        products: list[Product],
        filters: ComparisonFilters,
        stores_consulted: list[str] | None = None,
        stores_succeeded: list[str] | None = None,
        stores_failed: list[str] | None = None,
    ) -> tuple[list[Product], ComparisonSummary]:
        """Filtra y ordena productos y genera un resumen."""

        filtered_products = self._filter_products(
            products=products,
            filters=filters,
        )

        ordered_products = self._sort_products(
            products=filtered_products,
            price_order=filters.price_order,
        )

        summary = self._build_summary(
            original_products=products,
            filtered_products=ordered_products,
            stores_consulted=stores_consulted or [],
            stores_succeeded=stores_succeeded or [],
            stores_failed=stores_failed or [],
        )

        return ordered_products, summary

    def _filter_products(
        self,
        products: list[Product],
        filters: ComparisonFilters,
    ) -> list[Product]:
        """Aplica filtros de precio y envío."""

        result: list[Product] = []

        for product in products:
            if (
                filters.minimum_price is not None
                and product.precio < filters.minimum_price
            ):
                continue

            if (
                filters.maximum_price is not None
                and product.precio > filters.maximum_price
            ):
                continue

            if (
                filters.free_shipping_only
                and not product.envio_gratis
            ):
                continue

            result.append(product)

        return result

    def _sort_products(
        self,
        products: list[Product],
        price_order: PriceOrder,
    ) -> list[Product]:
        """Ordena productos sin modificar la lista original."""

        if price_order == PriceOrder.PRICE_ASC:
            return sorted(
                products,
                key=lambda product: product.precio,
            )

        if price_order == PriceOrder.PRICE_DESC:
            return sorted(
                products,
                key=lambda product: product.precio,
                reverse=True,
            )

        return list(products)

    def _build_summary(
        self,
        original_products: list[Product],
        filtered_products: list[Product],
        stores_consulted: list[str],
        stores_succeeded: list[str],
        stores_failed: list[str],
    ) -> ComparisonSummary:
        """Calcula las estadísticas de la comparación."""

        prices = [
            product.precio
            for product in filtered_products
        ]

        if not prices:
            return ComparisonSummary(
                stores_consulted=stores_consulted,
                stores_succeeded=stores_succeeded,
                stores_failed=stores_failed,
                products_before_filters=len(original_products),
                products_after_filters=0,
            )

        return ComparisonSummary(
            stores_consulted=stores_consulted,
            stores_succeeded=stores_succeeded,
            stores_failed=stores_failed,
            products_before_filters=len(original_products),
            products_after_filters=len(filtered_products),
            lowest_price=min(prices),
            highest_price=max(prices),
            average_price=round(
                sum(prices) / len(prices),
                2,
            ),
        )


price_comparison_service = PriceComparisonService()