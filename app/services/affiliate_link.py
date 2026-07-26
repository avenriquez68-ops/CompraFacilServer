"""Servicio para generar enlaces comerciales de productos."""

from app.affiliates.registry import AffiliateLinkBuilderRegistry


class AffiliateLinkService:
    """Genera enlaces comerciales según el proveedor del producto."""

    def __init__(
        self,
        registry: AffiliateLinkBuilderRegistry,
    ) -> None:
        """Inicializa el servicio con el registro de generadores."""

        self._registry = registry

    def build(
        self,
        provider_id: str,
        product_url: str,
    ) -> str:
        """Genera el enlace comercial correspondiente."""

        normalized_provider_id = provider_id.strip().lower()

        if not normalized_provider_id:
            raise ValueError(
                "El identificador del proveedor es obligatorio."
            )

        normalized_product_url = product_url.strip()

        if not normalized_product_url:
            raise ValueError(
                "La URL del producto es obligatoria."
            )

        return self._registry.build(
            provider_id=normalized_provider_id,
            product_url=normalized_product_url,
        )