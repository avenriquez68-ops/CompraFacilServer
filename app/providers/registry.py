"""Registro central de proveedores de productos."""

from app.core.config import Settings, settings
from app.infrastructure.clients.mercado_libre import MercadoLibreClient
from app.providers.base import ProductProvider
from app.providers.demo_store import DemoStoreProvider
from app.providers.mercado_libre import MercadoLibreProvider


class ProviderRegistry:
    """Administra los proveedores disponibles en la aplicación."""

    def __init__(
        self,
        providers: list[ProductProvider],
    ) -> None:
        """Inicializa el registro con una lista de proveedores."""

        self._providers = providers

    @property
    def providers(self) -> list[ProductProvider]:
        """Devuelve una copia de los proveedores registrados."""

        return self._providers.copy()

    def count(self) -> int:
        """Devuelve la cantidad de proveedores registrados."""

        return len(self._providers)

    def exists(self, provider_id: str) -> bool:
        """Indica si existe un proveedor con el identificador recibido."""

        return any(
            provider.info.provider_id == provider_id
            for provider in self._providers
        )

    def get(
        self,
        provider_id: str,
    ) -> ProductProvider | None:
        """Busca un proveedor por su identificador."""

        for provider in self._providers:
            if provider.info.provider_id == provider_id:
                return provider

        return None


def build_product_providers(
    mercado_libre: MercadoLibreClient,
    app_settings: Settings = settings,
) -> list[ProductProvider]:
    """Construye los proveedores habilitados por configuración."""

    providers: list[ProductProvider] = [
        MercadoLibreProvider(
            client=mercado_libre,
        ),
    ]

    if app_settings.enable_demo_store:
        providers.append(
            DemoStoreProvider()
        )

    return providers


def build_provider_registry(
    mercado_libre: MercadoLibreClient,
    app_settings: Settings = settings,
) -> ProviderRegistry:
    """Construye el registro de proveedores habilitados."""

    providers = build_product_providers(
        mercado_libre=mercado_libre,
        app_settings=app_settings,
    )

    return ProviderRegistry(
        providers=providers,
    )