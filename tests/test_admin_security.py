"""Pruebas de seguridad para endpoints administrativos."""

import pytest
from fastapi import HTTPException

from app.api import security


def test_admin_api_key_is_required(monkeypatch) -> None:
    """Debe rechazar solicitudes sin clave administrativa."""

    monkeypatch.setattr(
        security.settings,
        "admin_api_key",
        "test-secret",
    )

    with pytest.raises(HTTPException) as captured:
        security.require_admin_api_key(
            x_admin_key=None,
        )

    assert captured.value.status_code == 401


def test_admin_api_key_rejects_incorrect_key(
    monkeypatch,
) -> None:
    """Debe rechazar una clave administrativa incorrecta."""

    monkeypatch.setattr(
        security.settings,
        "admin_api_key",
        "test-secret",
    )

    with pytest.raises(HTTPException) as captured:
        security.require_admin_api_key(
            x_admin_key="incorrect-key",
        )

    assert captured.value.status_code == 401


def test_admin_api_key_accepts_valid_key(
    monkeypatch,
) -> None:
    """Debe aceptar la clave administrativa configurada."""

    monkeypatch.setattr(
        security.settings,
        "admin_api_key",
        "test-secret",
    )

    result = security.require_admin_api_key(
        x_admin_key="test-secret",
    )

    assert result is None

def test_admin_api_key_requires_server_configuration(
    monkeypatch,
) -> None:
    """Debe avisar cuando el servidor no tiene clave configurada."""

    monkeypatch.setattr(
        security.settings,
        "admin_api_key",
        "",
    )

    with pytest.raises(HTTPException) as captured:
        security.require_admin_api_key(
            x_admin_key="any-key",
        )

    assert captured.value.status_code == 503
    assert captured.value.detail == (
        "La clave administrativa no está configurada"
    )