"""Contrato común para proveedores de productos."""

from abc import ABC, abstractmethod

from app.schemas.provider import ProviderSearchResult


class ProductProvider(ABC):
    """Contrato que debe implementar cada tienda."""

    @property
    @abstractmethod
    def store_name(self) -> str:
        """Devuelve el nombre público de la tienda."""

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int,
    ) -> ProviderSearchResult:
        """Busca productos y devuelve resultados normalizados."""