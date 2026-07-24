"""Pruebas para el endpoint de proveedores."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_enabled_providers() -> None:
    """El endpoint debe devolver los proveedores habilitados."""

    response = client.get(
        "/api/v1/providers",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert len(data["providers"]) == 2

    store_names = [
        provider["store_name"]
        for provider in data["providers"]
    ]

    assert "Mercado Libre" in store_names
    assert "Tienda Demo" in store_names

    assert all(
        provider["enabled"] is True
        for provider in data["providers"]
    )