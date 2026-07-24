"""Contrato común para proveedores de productos."""

from abc import ABC, abstractmethod

from app.schemas.provider import ProviderSearchResult
from app.schemas.provider_info import ProviderInfo


class ProductProvider(ABC):
    """Contrato que debe implementar cada tienda."""

    @property
    @abstractmethod
    def store_name(self) -> str:
        """Devuelve el nombre público de la tienda."""

    @property
    @abstractmethod
    def info(self) -> ProviderInfo:
        """Devuelve la información descriptiva del proveedor."""

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int,
    ) -> ProviderSearchResult:
        """Busca productos y devuelve resultados normalizados."""