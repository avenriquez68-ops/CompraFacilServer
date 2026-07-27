"""Pruebas HTTP de estadísticas de clics afiliados."""

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import get_affiliate_click_repository
from app.main import app


client = TestClient(app)


class FakeAffiliateClickStatsRepository:
    """Repositorio simulado para las estadísticas."""

    def count_total(self, session: object) -> int:
        return 3

    def count_by_provider(
        self,
        session: object,
    ) -> dict[str, int]:
        return {
            "amazon": 1,
            "mercado_libre": 2,
        }

    def list_recent(
        self,
        session: object,
        limit: int = 20,
    ) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                id=3,
                provider_id="amazon",
                product_url="https://ejemplo.com/producto",
                destination_url="https://tienda.com/afiliado",
                created_at=datetime(
                    2026,
                    7,
                    27,
                    12,
                    0,
                    tzinfo=timezone.utc,
                ),
            )
        ]


def test_get_affiliate_click_stats() -> None:
    """Debe devolver el resumen de clics afiliados."""

    def override_repository() -> FakeAffiliateClickStatsRepository:
        return FakeAffiliateClickStatsRepository()

    app.dependency_overrides[
        get_affiliate_click_repository
    ] = override_repository

    try:
        response = client.get(
            "/api/v1/affiliate-clicks/stats",
            params={"limit": 5},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert body["total_clicks"] == 3
    assert body["clicks_by_provider"] == {
        "amazon": 1,
        "mercado_libre": 2,
    }
    assert len(body["recent_clicks"]) == 1
    assert body["recent_clicks"][0]["id"] == 3
    assert body["recent_clicks"][0]["provider_id"] == "amazon"

def test_affiliate_click_stats_rejects_invalid_limit() -> None:
    """Debe rechazar límites fuera del rango permitido."""

    for invalid_limit in (0, 101):
        response = client.get(
            "/api/v1/affiliate-clicks/stats",
            params={"limit": invalid_limit},
        )

        assert response.status_code == 422

        detail = response.json()["detail"]

        assert any(
            error["loc"][-1] == "limit"
            for error in detail
        )