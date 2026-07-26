"""Pruebas para el registro de generadores de afiliados."""

import pytest

from app.affiliates.base import (
    AffiliateLinkBuilder,
    PassthroughAffiliateLinkBuilder,
)
from app.affiliates.registry import (
    AffiliateLinkBuilderRegistry,
    build_affiliate_link_builder_registry,
)


class FakeAffiliateLinkBuilder(AffiliateLinkBuilder):
    """Generador falso utilizado únicamente en pruebas."""

    def __init__(
        self,
        provider_id: str,
        prefix: str,
    ) -> None:
        self._provider_id = provider_id
        self._prefix = prefix

    @property
    def provider_id(self) -> str:
        """Devuelve el identificador de prueba."""

        return self._provider_id

    def build(self, product_url: str) -> str:
        """Genera una dirección predecible para la prueba."""

        return f"{self._prefix}{product_url}"


def test_registry_counts_registered_builders() -> None:
    """Debe informar la cantidad de generadores registrados."""

    registry = AffiliateLinkBuilderRegistry(
        builders=[
            PassthroughAffiliateLinkBuilder(
                provider_id="mercado_libre"
            ),
            PassthroughAffiliateLinkBuilder(
                provider_id="demo_store"
            ),
        ],
    )

    assert registry.count() == 2


def test_registry_returns_copy_of_builders() -> None:
    """Modificar la lista devuelta no debe alterar el registro."""

    registry = AffiliateLinkBuilderRegistry(
        builders=[
            PassthroughAffiliateLinkBuilder(
                provider_id="mercado_libre"
            ),
        ],
    )

    builders = registry.builders
    builders.clear()

    assert registry.count() == 1


def test_registry_detects_existing_provider() -> None:
    """Debe reconocer identificadores registrados."""

    registry = AffiliateLinkBuilderRegistry(
        builders=[
            PassthroughAffiliateLinkBuilder(
                provider_id="mercado_libre"
            ),
        ],
    )

    assert registry.exists("mercado_libre") is True
    assert registry.exists("  MERCADO_LIBRE  ") is True
    assert registry.exists("amazon") is False


def test_registry_gets_builder_by_provider_id() -> None:
    """Debe devolver el generador correspondiente."""

    builder = PassthroughAffiliateLinkBuilder(
        provider_id="mercado_libre"
    )

    registry = AffiliateLinkBuilderRegistry(
        builders=[builder],
    )

    result = registry.get(" mercado_libre ")

    assert result is builder


def test_registry_returns_none_for_unknown_provider() -> None:
    """Debe devolver None cuando no existe el generador."""

    registry = AffiliateLinkBuilderRegistry(
        builders=[],
    )

    assert registry.get("amazon") is None


def test_registry_builds_url_with_registered_builder() -> None:
    """Debe utilizar el generador registrado."""

    registry = AffiliateLinkBuilderRegistry(
        builders=[
            FakeAffiliateLinkBuilder(
                provider_id="mercado_libre",
                prefix="affiliate:",
            ),
        ],
    )

    result = registry.build(
        provider_id="mercado_libre",
        product_url="https://example.com/producto/123",
    )

    assert result == (
        "affiliate:https://example.com/producto/123"
    )


def test_registry_uses_passthrough_for_unknown_provider() -> None:
    """Un proveedor desconocido debe conservar la URL original."""

    registry = AffiliateLinkBuilderRegistry(
        builders=[],
    )

    product_url = "https://example.com/producto/123"

    result = registry.build(
        provider_id="future_store",
        product_url=product_url,
    )

    assert result == product_url


def test_registry_rejects_empty_provider_id() -> None:
    """No debe crearse un respaldo con identificador vacío."""

    registry = AffiliateLinkBuilderRegistry(
        builders=[],
    )

    with pytest.raises(
        ValueError,
        match="El identificador del proveedor es obligatorio",
    ):
        registry.get_or_passthrough("   ")


def test_registry_rejects_duplicate_provider_ids() -> None:
    """No debe permitirse más de un generador por proveedor."""

    first_builder = PassthroughAffiliateLinkBuilder(
        provider_id="mercado_libre"
    )
    second_builder = PassthroughAffiliateLinkBuilder(
        provider_id="mercado_libre"
    )

    with pytest.raises(
        ValueError,
        match=(
            "Ya existe un generador de enlaces para "
            "el proveedor 'mercado_libre'"
        ),
    ):
        AffiliateLinkBuilderRegistry(
            builders=[
                first_builder,
                second_builder,
            ],
        )


def test_default_registry_contains_initial_providers() -> None:
    """El registro predeterminado debe incluir las tiendas actuales."""

    registry = build_affiliate_link_builder_registry()

    assert registry.exists("mercado_libre") is True
    assert registry.exists("demo_store") is True
    assert registry.count() == 2