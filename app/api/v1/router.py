"""Enrutador principal de la versión 1 de la API."""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.search import router as search_router
from app.api.v1.providers import router as providers_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(search_router)
api_router.include_router(providers_router)