"""Endpoint para verificar el estado del servidor."""

from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(tags=["Estado"])


@router.get(
    "/health",
    summary="Verificar el estado de la API",
    description="Confirma que Compra Fácil Server está funcionando.",
)
async def health_check() -> dict[str, str]:
    """Devuelve el estado actual del servidor."""

    return {
        "status": "ok",
        "service": "Compra Fácil Server",
        "timestamp": datetime.now(UTC).isoformat(),
    }