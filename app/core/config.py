"""Configuración general de Compra Fácil Server."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración cargada desde variables de entorno."""

    app_name: str = "Compra Fácil Server"
    app_version: str = "1.3.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    admin_api_key: str = ""

    mercado_libre_base_url: str = "https://api.mercadolibre.com"
    mercado_libre_site_id: str = "MLM"
    mercado_libre_access_token: str = ""
    mercado_libre_timeout_seconds: float = 10.0
    mercado_libre_affiliate_id: str = ""
    mercado_libre_client_id: str = ""
    mercado_libre_client_secret: str = ""
    mercado_libre_authorization_url: str = (
        "https://auth.mercadolibre.com.mx/authorization"
    )
    mercado_libre_token_url: str = (
        "https://api.mercadolibre.com/oauth/token"
    )
    mercado_libre_redirect_uri: str = (
        "https://api.dameprecio.shop"
        "/api/v1/auth/mercado-libre/callback"
    )

    amazon_associate_tag: str = ""

    walmart_affiliate_id: str = ""

    enable_demo_store: bool = True

    database_url: str = "sqlite:///./compra_facil.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Devuelve una única instancia de configuración."""

    return Settings()


settings = get_settings()