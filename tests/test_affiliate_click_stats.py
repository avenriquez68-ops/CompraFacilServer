"""Pruebas HTTP de estadísticas de clics afiliados."""

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import get_affiliate_click_repository
from app.main import app
import pytest
from app.api.security import require_admin_api_key


client = TestClient(app)

@pytest.fixture(autouse=True)
def allow_admin_access():
    """Autoriza las pruebas que no evalúan seguridad."""

    app.dependency_overrides[
        require_admin_api_key
    ] = lambda: None

    yield

    app.dependency_overrides.pop(
        require_admin_api_key,
        None,
    )

class FakeAffiliateClickStatsRepository:
    """Repositorio simulado para las estadísticas."""

    def count_total(
        self,
        session: object,
        provider_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> int:
        return 3

    def count_by_provider(
        self,
        session: object,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict[str, int]:
        return {
            "amazon": 1,
            "mercado_libre": 2,
        }

    def list_recent(
        self,
        session: object,
        limit: int = 20,
        provider_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
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

def test_affiliate_click_stats_filters_by_provider() -> None:
    """Debe devolver estadísticas de un solo proveedor."""

    class ProviderFilteringRepository(
        FakeAffiliateClickStatsRepository
    ):
        def count_total(
            self,
            session: object,
            provider_id: str | None = None,
            date_from: datetime | None = None,
            date_to: datetime | None = None,
        ) -> int:
            if provider_id == "mercado_libre":
                return 2

            return 3

        def list_recent(
            self,
            session: object,
            limit: int = 20,
            provider_id: str | None = None,
            date_from: datetime | None = None,
            date_to: datetime | None = None,
        ) -> list[SimpleNamespace]:
            if provider_id == "mercado_libre":
                return [
                    SimpleNamespace(
                        id=2,
                        provider_id="mercado_libre",
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

            return super().list_recent(
                session=session,
                limit=limit,
                provider_id=provider_id,
                date_from=date_from,
                date_to=date_to,
            )

    def override_repository() -> ProviderFilteringRepository:
        return ProviderFilteringRepository()

    app.dependency_overrides[
        get_affiliate_click_repository
    ] = override_repository

    try:
        response = client.get(
            "/api/v1/affiliate-clicks/stats",
            params={
                "provider_id": "mercado_libre",
                "limit": 5,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert body["total_clicks"] == 2
    assert body["clicks_by_provider"] == {
        "mercado_libre": 2,
    }
    assert len(body["recent_clicks"]) == 1
    assert (
        body["recent_clicks"][0]["provider_id"]
        == "mercado_libre"
    )

def test_affiliate_click_stats_filters_by_date_range() -> None:
    """Debe enviar el rango de fechas al repositorio."""

    received_dates: dict[
        str,
        tuple[datetime | None, datetime | None],
    ] = {}

    class DateFilteringRepository(
        FakeAffiliateClickStatsRepository
    ):
        def count_total(
            self,
            session: object,
            provider_id: str | None = None,
            date_from: datetime | None = None,
            date_to: datetime | None = None,
        ) -> int:
            received_dates["total"] = (
                date_from,
                date_to,
            )
            return 1

        def count_by_provider(
            self,
            session: object,
            date_from: datetime | None = None,
            date_to: datetime | None = None,
        ) -> dict[str, int]:
            received_dates["providers"] = (
                date_from,
                date_to,
            )
            return {"amazon": 1}

        def list_recent(
            self,
            session: object,
            limit: int = 20,
            provider_id: str | None = None,
            date_from: datetime | None = None,
            date_to: datetime | None = None,
        ) -> list[SimpleNamespace]:
            received_dates["recent"] = (
                date_from,
                date_to,
            )

            return super().list_recent(
                session=session,
                limit=limit,
                provider_id=provider_id,
                date_from=date_from,
                date_to=date_to,
            )

    def override_repository() -> DateFilteringRepository:
        return DateFilteringRepository()

    app.dependency_overrides[
        get_affiliate_click_repository
    ] = override_repository

    try:
        response = client.get(
            "/api/v1/affiliate-clicks/stats",
            params={
                "date_from": "2026-07-10T00:00:00Z",
                "date_to": "2026-07-31T23:59:59Z",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["total_clicks"] == 1
    assert received_dates["total"][0] is not None
    assert received_dates["total"][1] is not None
    assert received_dates["providers"][0] is not None
    assert received_dates["providers"][1] is not None
    assert received_dates["recent"][0] is not None
    assert received_dates["recent"][1] is not None

def test_affiliate_click_stats_rejects_inverted_dates() -> None:
    """Debe rechazar un rango de fechas invertido."""

    def override_repository() -> FakeAffiliateClickStatsRepository:
        return FakeAffiliateClickStatsRepository()

    app.dependency_overrides[
        get_affiliate_click_repository
    ] = override_repository

    try:
        response = client.get(
            "/api/v1/affiliate-clicks/stats",
            params={
                "date_from": "2026-07-31T23:59:59Z",
                "date_to": "2026-07-01T00:00:00Z",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "date_from no puede ser posterior a date_to"
        )
    }