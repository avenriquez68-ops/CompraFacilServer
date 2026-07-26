"""Contratos comunes para generar enlaces de afiliado."""

from abc import ABC, abstractmethod
from urllib.parse import urlparse


class AffiliateLinkBuilder(ABC):
    """Contrato para transformar URLs originales en enlaces comerciales."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Devuelve el identificador interno del proveedor."""

    @abstractmethod
    def build(self, product_url: str) -> str:
        """Construye el enlace de afiliado para un producto."""


class PassthroughAffiliateLinkBuilder(AffiliateLinkBuilder):
    """Devuelve la URL original sin aplicar parámetros de afiliación."""

    def __init__(self, provider_id: str) -> None:
        normalized_provider_id = provider_id.strip().lower()

        if not normalized_provider_id:
            raise ValueError("El identificador del proveedor es obligatorio.")

        self._provider_id = normalized_provider_id

    @property
    def provider_id(self) -> str:
        """Devuelve el identificador interno del proveedor."""

        return self._provider_id

    def build(self, product_url: str) -> str:
        """Valida y devuelve la URL original."""

        normalized_url = product_url.strip()

        if not normalized_url:
            raise ValueError("La URL del producto es obligatoria.")

        parsed_url = urlparse(normalized_url)

        if parsed_url.scheme not in {"http", "https"}:
            raise ValueError(
                "La URL del producto debe utilizar HTTP o HTTPS."
            )

        if not parsed_url.netloc:
            raise ValueError(
                "La URL del producto debe contener un dominio válido."
            )

        return normalized_url