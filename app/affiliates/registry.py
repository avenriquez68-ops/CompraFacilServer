"""Registro central de generadores de enlaces de afiliado."""

from app.affiliates.base import (
    AffiliateLinkBuilder,
    PassthroughAffiliateLinkBuilder,
)


class AffiliateLinkBuilderRegistry:
    """Administra los generadores de enlaces por proveedor."""

    def __init__(
        self,
        builders: list[AffiliateLinkBuilder],
    ) -> None:
        """Inicializa el registro con los generadores disponibles."""

        self._builders: dict[str, AffiliateLinkBuilder] = {}

        for builder in builders:
            provider_id = builder.provider_id

            if provider_id in self._builders:
                raise ValueError(
                    "Ya existe un generador de enlaces para "
                    f"el proveedor '{provider_id}'."
                )

            self._builders[provider_id] = builder

    @property
    def builders(self) -> list[AffiliateLinkBuilder]:
        """Devuelve una copia de los generadores registrados."""

        return list(self._builders.values())

    def count(self) -> int:
        """Devuelve la cantidad de generadores registrados."""

        return len(self._builders)

    def exists(self, provider_id: str) -> bool:
        """Indica si existe un generador para el proveedor."""

        normalized_id = provider_id.strip().lower()

        if not normalized_id:
            return False

        return normalized_id in self._builders

    def get(
        self,
        provider_id: str,
    ) -> AffiliateLinkBuilder | None:
        """Busca un generador por el identificador del proveedor."""

        normalized_id = provider_id.strip().lower()

        if not normalized_id:
            return None

        return self._builders.get(normalized_id)

    def get_or_passthrough(
        self,
        provider_id: str,
    ) -> AffiliateLinkBuilder:
        """Devuelve el generador registrado o uno neutral."""

        normalized_id = provider_id.strip().lower()

        if not normalized_id:
            raise ValueError(
                "El identificador del proveedor es obligatorio."
            )

        builder = self.get(normalized_id)

        if builder is not None:
            return builder

        return PassthroughAffiliateLinkBuilder(
            provider_id=normalized_id,
        )

    def build(
        self,
        provider_id: str,
        product_url: str,
    ) -> str:
        """Construye un enlace mediante el generador correspondiente."""

        builder = self.get_or_passthrough(provider_id)

        return builder.build(product_url)


def build_affiliate_link_builder_registry(
) -> AffiliateLinkBuilderRegistry:
    """Construye el registro inicial de generadores."""

    builders: list[AffiliateLinkBuilder] = [
        PassthroughAffiliateLinkBuilder(
            provider_id="mercado_libre",
        ),
        PassthroughAffiliateLinkBuilder(
            provider_id="demo_store",
        ),
    ]

    return AffiliateLinkBuilderRegistry(
        builders=builders,
    )