"""Endpoints de autenticación OAuth con Mercado Libre."""

import base64
import hashlib
import secrets
from urllib.parse import urlencode

from typing import Annotated
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Query,
)
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_mercado_libre_credential_repository,
    get_mercado_libre_oauth_client,
)
from app.infrastructure.clients.mercado_libre_oauth import (
    MercadoLibreOAuthClient,
    MercadoLibreOAuthError,
)
from app.infrastructure.database.connection import (
    get_database_session,
)
from app.repositories.mercado_libre_credential import (
    MercadoLibreCredentialRepository,
)

from app.core.config import settings


router = APIRouter(
    prefix="/auth/mercado-libre",
    tags=["Autenticación"],
)


def create_pkce_values() -> tuple[str, str]:
    """Genera el verificador y el desafío PKCE S256."""

    code_verifier = secrets.token_urlsafe(48)

    digest = hashlib.sha256(
        code_verifier.encode("ascii")
    ).digest()

    code_challenge = base64.urlsafe_b64encode(
        digest
    ).rstrip(b"=").decode("ascii")

    return code_verifier, code_challenge


@router.get(
    "/login",
    response_class=RedirectResponse,
    summary="Iniciar sesión con Mercado Libre",
)
def login_with_mercado_libre() -> RedirectResponse:
    """Redirige al usuario hacia la autorización de Mercado Libre."""

    if (
        not settings.mercado_libre_client_id
        or not settings.mercado_libre_client_secret
    ):
        raise HTTPException(
            status_code=503,
            detail=(
                "La autenticación de Mercado Libre "
                "no está configurada."
            ),
        )

    state = secrets.token_urlsafe(32)

    state = secrets.token_urlsafe(32)
    code_verifier, code_challenge = create_pkce_values()

    parameters = urlencode(
        {
            "response_type": "code",
            "client_id": settings.mercado_libre_client_id,
            "redirect_uri": settings.mercado_libre_redirect_uri,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
    )

    response = RedirectResponse(
        url=(
            f"{settings.mercado_libre_authorization_url}"
            f"?{parameters}"
        ),
        status_code=307,
    )

    cookie_path = (
        f"{settings.api_v1_prefix}/auth/mercado-libre"
    )

    response.set_cookie(
        key="ml_oauth_state",
        value=state,
        max_age=600,
        httponly=True,
        secure=True,
        samesite="lax",
        path=cookie_path,
    )
    response.set_cookie(
        key="ml_pkce_verifier",
        value=code_verifier,
        max_age=600,
        httponly=True,
        secure=True,
        samesite="lax",
        path=cookie_path,
    )

    return response

@router.get(
    "/callback",
    summary="Completar autenticación con Mercado Libre",
)
@router.get(
    "/callback",
    summary="Completar autenticación con Mercado Libre",
)
async def mercado_libre_callback(
    code: Annotated[
        str,
        Query(min_length=1),
    ],
    state: Annotated[
        str,
        Query(min_length=1),
    ],
    session: Annotated[
        Session,
        Depends(get_database_session),
    ],
    oauth_client: Annotated[
        MercadoLibreOAuthClient,
        Depends(get_mercado_libre_oauth_client),
    ],
    repository: Annotated[
        MercadoLibreCredentialRepository,
        Depends(get_mercado_libre_credential_repository),
    ],
    expected_state: Annotated[
        str | None,
        Cookie(alias="ml_oauth_state"),
    ] = None,
    code_verifier: Annotated[
        str | None,
        Cookie(alias="ml_pkce_verifier"),
    ] = None,
) -> JSONResponse:
    """Intercambia el código y guarda las credenciales."""

    if expected_state is None or code_verifier is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "No existe una solicitud OAuth "
                "pendiente."
            ),
        )

    if not secrets.compare_digest(state, expected_state):
        raise HTTPException(
            status_code=400,
            detail="El parámetro state no es válido.",
        )

    try:
        token = await oauth_client.exchange_code(
            code=code,
            code_verifier=code_verifier,
        )
    except MercadoLibreOAuthError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    credential = repository.save(
        session=session,
        token=token,
    )

    response = JSONResponse(
        content={
            "status": "connected",
            "provider_id": "mercado_libre",
            "user_id": credential.user_id,
        }
    )

    cookie_path = (
        f"{settings.api_v1_prefix}/auth/mercado-libre"
    )

    response.delete_cookie(
        key="ml_oauth_state",
        path=cookie_path,
        secure=True,
        httponly=True,
        samesite="lax",
    )
    response.delete_cookie(
        key="ml_pkce_verifier",
        path=cookie_path,
        secure=True,
        httponly=True,
        samesite="lax",
    )

    return response
    """Valida la respuesta recibida desde Mercado Libre."""

    if expected_state is None or code_verifier is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "No existe una solicitud OAuth "
                "pendiente."
            ),
        )

    if not secrets.compare_digest(state, expected_state):
        raise HTTPException(
            status_code=400,
            detail="El parámetro state no es válido.",
        )

    return {
        "status": "validated",
        "code": code,
    }