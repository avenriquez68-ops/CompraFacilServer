"""Pruebas HTTP de seguridad para estadísticas."""

from fastapi.testclient import TestClient

from app.api import security
from app.api.dependencies import get_affiliate_click_repository
from app.main import app


client = TestClient(app)


class EmptyStatsRepository:
    """Repositorio simulado sin clics."""

    def count_total(self, **kwargs) -> int:
        return 0

    def count_by_provider(self, **kwargs) -> dict[str, int]:
        return {}

    def list_recent(self, **kwargs) -> list[object]:
        return []


def override_repository() -> EmptyStatsRepository:
    return EmptyStatsRepository()


def test_stats_endpoint_requires_admin_key(
    monkeypatch,
) -> None:
    """Debe rechazar solicitudes sin clave."""

    monkeypatch.setattr(
        security.settings,
        "admin_api_key",
        "test-secret",
    )

    app.dependency_overrides[
        get_affiliate_click_repository
    ] = override_repository

    try:
        response = client.get(
            "/api/v1/affiliate-clicks/stats"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Clave administrativa inválida"
    }


def test_stats_endpoint_accepts_valid_admin_key(
    monkeypatch,
) -> None:
    """Debe aceptar una clave administrativa válida."""

    monkeypatch.setattr(
        security.settings,
        "admin_api_key",
        "test-secret",
    )

    app.dependency_overrides[
        get_affiliate_click_repository
    ] = override_repository

    try:
        response = client.get(
            "/api/v1/affiliate-clicks/stats",
            headers={
                "X-Admin-Key": "test-secret",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "total_clicks": 0,
        "clicks_by_provider": {},
        "recent_clicks": [],
    }