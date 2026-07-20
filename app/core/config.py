"""Configuración general de Compra Fácil Server."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Valores básicos de configuración de la API."""

    app_name: str = "Compra Fácil Server"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"


settings = Settings()