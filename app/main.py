"""Punto de entrada de Compra Fácil Server."""

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.infrastructure.database.initializer import initialize_database

initialize_database()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API para buscar y comparar productos de diferentes tiendas en línea."
    ),
)

app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)


@app.get(
    "/",
    tags=["Inicio"],
    summary="Información general de la API",
)
async def root() -> dict[str, str]:
    """Devuelve información básica y la ruta de la documentación."""

    return {
        "message": "Compra Fácil Server está funcionando",
        "version": settings.app_version,
        "documentation": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }