"""Enrutador principal de la versión 1 de la API."""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.providers import router as providers_router
from app.api.v1.redirect import router as redirect_router
from app.api.v1.search import router as search_router
from app.api.v1.affiliate_clicks import (
    router as affiliate_clicks_router,
)
from app.api.v1.mercado_libre_auth import (
    router as mercado_libre_auth_router,
)

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(search_router)
api_router.include_router(providers_router)
api_router.include_router(redirect_router)
api_router.include_router(affiliate_clicks_router)
api_router.include_router(mercado_libre_auth_router)