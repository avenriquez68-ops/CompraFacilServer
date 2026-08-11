"""Pruebas del arranque de la aplicación."""

from fastapi.testclient import TestClient

import app.main as main_module


def test_app_initializes_database_on_startup(
    monkeypatch,
) -> None:
    """Debe inicializar la base de datos al arrancar."""

    initialization_calls: list[bool] = []

    def fake_initialize_database() -> None:
        initialization_calls.append(True)

    monkeypatch.setattr(
        main_module,
        "initialize_database",
        fake_initialize_database,
        raising=False,
    )

    with TestClient(main_module.app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert initialization_calls == [True]

def test_app_allows_dameprecio_frontend_origin() -> None:
    """Debe permitir solicitudes desde el frontend público."""

    with TestClient(main_module.app) as client:
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "https://dameprecio.shop",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "https://dameprecio.shop"
    )