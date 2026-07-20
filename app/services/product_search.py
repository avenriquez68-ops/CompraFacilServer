"""Servicio encargado de buscar productos."""

from app.schemas.product import Product


PRODUCTS: tuple[Product, ...] = (
    Product(
        id="ml-001",
        nombre="Laptop Lenovo IdeaPad 15",
        precio=15499.99,
        moneda="MXN",
        tienda="Mercado Libre",
        url="https://www.mercadolibre.com.mx/",
        calificacion=4.7,
        numero_resenas=253,
    ),
    Product(
        id="amazon-001",
        nombre="Laptop HP 14 pulgadas",
        precio=13299.00,
        moneda="MXN",
        tienda="Amazon México",
        url="https://www.amazon.com.mx/",
        calificacion=4.5,
        numero_resenas=187,
    ),
    Product(
        id="walmart-001",
        nombre="Laptop Acer Aspire 3",
        precio=11999.00,
        moneda="MXN",
        tienda="Walmart México",
        url="https://www.walmart.com.mx/",
        calificacion=4.4,
        numero_resenas=86,
    ),
    Product(
        id="ml-002",
        nombre="Audífonos inalámbricos Sony",
        precio=1899.00,
        moneda="MXN",
        tienda="Mercado Libre",
        url="https://www.mercadolibre.com.mx/",
        calificacion=4.8,
        numero_resenas=641,
    ),
    Product(
        id="amazon-002",
        nombre="Audífonos Bluetooth JBL",
        precio=1299.00,
        moneda="MXN",
        tienda="Amazon México",
        url="https://www.amazon.com.mx/",
        calificacion=4.6,
        numero_resenas=329,
    ),
    Product(
        id="walmart-002",
        nombre="Cafetera programable Oster",
        precio=1099.00,
        moneda="MXN",
        tienda="Walmart México",
        url="https://www.walmart.com.mx/",
        calificacion=4.3,
        numero_resenas=94,
    ),
)


class ProductSearchService:
    """Contiene la lógica para buscar productos."""

    def search(self, query: str) -> list[Product]:
        """
        Busca productos cuyo nombre o tienda contenga el texto indicado.

        La comparación no distingue entre mayúsculas y minúsculas.
        """

        normalized_query = query.strip().casefold()

        return [
            product
            for product in PRODUCTS
            if normalized_query in product.nombre.casefold()
            or normalized_query in product.tienda.casefold()
        ]


product_search_service = ProductSearchService()