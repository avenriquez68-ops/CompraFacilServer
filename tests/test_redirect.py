"""Pruebas del endpoint de redirección."""

from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_affiliate_link_service


client = TestClient(app)

class FakeAffiliateLinkService:
    """Servicio simulado para probar el endpoint."""

    def build(
        self,
        provider_id: str,
        product_url: str,
    ) -> str:
        return product_url


def test_redirect_returns_http_307() -> None:
    """Debe devolver una redirección HTTP."""

    def override_service() -> FakeAffiliateLinkService:
        return FakeAffiliateLinkService()

    app.dependency_overrides[
        get_affiliate_link_service
    ] = override_service

    try:
        response = client.get(
            "/api/v1/redirect",
            params={
                "provider_id": "mercado_libre",
                "product_url": "https://www.mercadolibre.com.mx",
            },
            follow_redirects=False,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 307

    assert (
        response.headers["location"]
        == "https://www.mercadolibre.com.mx"
    )

def test_redirect_rejects_invalid_product_url() -> None:
    response = client.get(
        "/api/v1/redirect",
        params={
            "provider_id": "mercado_libre",
            "product_url": "esto-no-es-una-url",
        },
        follow_redirects=False,
    )

    assert response.status_code == 422

    detail = response.json()["detail"]

    assert isinstance(detail, str)
    assert "url" in detail.lower()

def test_redirect_rejects_missing_provider_id() -> None:
    response = client.get(
        "/api/v1/redirect",
        params={
            "product_url": "https://www.mercadolibre.com.mx",
        },
        follow_redirects=False,
    )

    assert response.status_code == 422

    detail = response.json()["detail"]

    assert isinstance(detail, list)
    assert any(
        error["loc"][-1] == "provider_id"
        and error["type"] == "missing"
        for error in detail
    )

def test_redirect_rejects_missing_product_url() -> None:
    response = client.get(
        "/api/v1/redirect",
        params={
            "provider_id": "mercado_libre",
        },
        follow_redirects=False,
    )

    assert response.status_code == 422

    detail = response.json()["detail"]

    assert isinstance(detail, list)
    assert any(
        error["loc"][-1] == "product_url"
        and error["type"] == "missing"
        for error in detail
    )

def test_redirect_converts_service_value_error_to_422() -> None:
    """Debe convertir un ValueError del servicio en HTTP 422."""

    class FailingAffiliateLinkService:
        def build(
            self,
            provider_id: str,
            product_url: str,
        ) -> str:
            raise ValueError("Proveedor no compatible")

    def override_service() -> FailingAffiliateLinkService:
        return FailingAffiliateLinkService()

    app.dependency_overrides[
        get_affiliate_link_service
    ] = override_service

    try:
        response = client.get(
            "/api/v1/redirect",
            params={
                "provider_id": "proveedor_desconocido",
                "product_url": "https://www.ejemplo.com/producto",
            },
            follow_redirects=False,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Proveedor no compatible"
    }

def test_redirect_returns_500_for_unexpected_error() -> None:
    """Debe responder 500 ante una falla inesperada."""

    class UnexpectedErrorService:
        def build(
            self,
            provider_id: str,
            product_url: str,
        ) -> str:
            raise RuntimeError("Falla inesperada")

    def override_service() -> UnexpectedErrorService:
        return UnexpectedErrorService()

    app.dependency_overrides[
        get_affiliate_link_service
    ] = override_service

    error_client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    try:
        response = error_client.get(
            "/api/v1/redirect",
            params={
                "provider_id": "mercado_libre",
                "product_url": "https://www.mercadolibre.com.mx",
            },
            follow_redirects=False,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500