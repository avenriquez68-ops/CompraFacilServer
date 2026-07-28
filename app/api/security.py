"""Seguridad para endpoints administrativos."""

from secrets import compare_digest
from typing import Annotated

from fastapi import Header, HTTPException

from app.core.config import settings


def require_admin_api_key(
    x_admin_key: Annotated[
        str | None,
        Header(
            alias="X-Admin-Key",
            description="Clave de acceso administrativo.",
        ),
    ] = None,
) -> None:
    """Valida la clave administrativa enviada por el cliente."""

    expected_key = settings.admin_api_key

    if not expected_key:
        raise HTTPException(
            status_code=503,
            detail="La clave administrativa no está configurada",
        )

    if (
        x_admin_key is None
        or not compare_digest(x_admin_key, expected_key)
    ):
        raise HTTPException(
            status_code=401,
            detail="Clave administrativa inválida",
            headers={
                "WWW-Authenticate": "ApiKey",
            },
        )