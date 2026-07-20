"""Pruebas del endpoint de búsqueda."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_laptop_returns_three_products() -> None:
    """La búsqueda de laptop debe encontrar tres productos."""

    response = client.get(
        "/api/v1/search",
        params={"q": "laptop"},
    )

    assert response.status_code == 200

    products = response.json()

    assert len(products) == 3
    assert all("laptop" in product["nombre"].lower() for product in products)


def test_search_without_results_returns_empty_list() -> None:
    """Una búsqueda inexistente debe devolver una lista vacía."""

    response = client.get(
        "/api/v1/search",
        params={"q": "producto inexistente"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_search_query_requires_two_characters() -> None:
    """La consulta debe tener al menos dos caracteres."""

    response = client.get(
        "/api/v1/search",
        params={"q": "a"},
    )

    assert response.status_code == 422