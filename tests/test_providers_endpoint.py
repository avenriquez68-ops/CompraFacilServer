"""Pruebas para el endpoint de proveedores."""

from fastapi.testclient import TestClient

from app.api.dependencies import get_provider_registry
from app.providers.registry import ProviderRegistry

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


def test_providers_endpoint_returns_provider_metadata() -> None:
    """El endpoint debe devolver las capacidades de cada proveedor."""

    response = client.get("/api/v1/providers")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] >= 1
    assert len(data["providers"]) == data["total"]

    first_provider = data["providers"][0]

    assert "provider_id" in first_provider
    assert "store_name" in first_provider
    assert "provider_type" in first_provider
    assert "country_code" in first_provider
    assert "supports_free_shipping" in first_provider
    assert "supports_ratings" in first_provider
    assert "is_demo" in first_provider
    assert first_provider["enabled"] is True

def test_providers_endpoint_uses_dependency_override() -> None:
    """El endpoint debe utilizar el registro inyectado."""

    empty_registry = ProviderRegistry(
        providers=[],
    )

    def override_provider_registry() -> ProviderRegistry:
        return empty_registry

    app.dependency_overrides[
        get_provider_registry
    ] = override_provider_registry

    try:
        response = client.get(
            "/api/v1/providers",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 0
        assert data["providers"] == []

    finally:
        app.dependency_overrides.pop(
            get_provider_registry,
            None,
        )