"""Pruebas para el servicio de enlaces comerciales."""

import pytest

from app.affiliates.base import AffiliateLinkBuilder
from app.affiliates.registry import AffiliateLinkBuilderRegistry
from app.services.affiliate_link import AffiliateLinkService


class FakeAffiliateLinkBuilder(AffiliateLinkBuilder):
    """Generador controlado utilizado en las pruebas."""

    def __init__(
        self,
        provider_id: str,
    ) -> None:
        self._provider_id = provider_id
        self.received_product_url: str | None = None

    @property
    def provider_id(self) -> str:
        """Devuelve el identificador del proveedor falso."""

        return self._provider_id

    def build(
        self,
        product_url: str,
    ) -> str:
        """Devuelve un enlace predecible para las pruebas."""

        self.received_product_url = product_url

        return (
            "https://affiliate.example.com/redirect"
            f"?url={product_url}"
        )


def test_service_uses_registered_builder() -> None:
    """Debe utilizar el generador correspondiente al proveedor."""

    builder = FakeAffiliateLinkBuilder(
        provider_id="mercado_libre",
    )

    registry = AffiliateLinkBuilderRegistry(
        builders=[builder],
    )

    service = AffiliateLinkService(
        registry=registry,
    )

    result = service.build(
        provider_id="mercado_libre",
        product_url="https://example.com/producto/123",
    )

    assert result == (
        "https://affiliate.example.com/redirect"
        "?url=https://example.com/producto/123"
    )

    assert builder.received_product_url == (
        "https://example.com/producto/123"
    )


def test_service_normalizes_provider_id() -> None:
    """Debe eliminar espacios y normalizar el identificador."""

    builder = FakeAffiliateLinkBuilder(
        provider_id="mercado_libre",
    )

    registry = AffiliateLinkBuilderRegistry(
        builders=[builder],
    )

    service = AffiliateLinkService(
        registry=registry,
    )

    result = service.build(
        provider_id="  MERCADO_LIBRE  ",
        product_url="https://example.com/producto/123",
    )

    assert result.startswith(
        "https://affiliate.example.com/redirect"
    )


def test_service_normalizes_product_url_spaces() -> None:
    """Debe eliminar espacios exteriores de la URL."""

    builder = FakeAffiliateLinkBuilder(
        provider_id="mercado_libre",
    )

    registry = AffiliateLinkBuilderRegistry(
        builders=[builder],
    )

    service = AffiliateLinkService(
        registry=registry,
    )

    service.build(
        provider_id="mercado_libre",
        product_url=(
            "  https://example.com/producto/123  "
        ),
    )

    assert builder.received_product_url == (
        "https://example.com/producto/123"
    )


def test_service_uses_passthrough_for_unknown_provider() -> None:
    """Debe conservar la URL para proveedores sin generador."""

    registry = AffiliateLinkBuilderRegistry(
        builders=[],
    )

    service = AffiliateLinkService(
        registry=registry,
    )

    product_url = "https://future-store.example/producto/123"

    result = service.build(
        provider_id="future_store",
        product_url=product_url,
    )

    assert result == product_url


def test_service_rejects_empty_provider_id() -> None:
    """Debe rechazar identificadores vacíos."""

    registry = AffiliateLinkBuilderRegistry(
        builders=[],
    )

    service = AffiliateLinkService(
        registry=registry,
    )

    with pytest.raises(
        ValueError,
        match="El identificador del proveedor es obligatorio",
    ):
        service.build(
            provider_id="   ",
            product_url="https://example.com/producto/123",
        )


def test_service_rejects_empty_product_url() -> None:
    """Debe rechazar direcciones vacías."""

    registry = AffiliateLinkBuilderRegistry(
        builders=[],
    )

    service = AffiliateLinkService(
        registry=registry,
    )

    with pytest.raises(
        ValueError,
        match="La URL del producto es obligatoria",
    ):
        service.build(
            provider_id="mercado_libre",
            product_url="   ",
        )


def test_service_rejects_invalid_product_url() -> None:
    """El generador neutral debe validar la dirección recibida."""

    registry = AffiliateLinkBuilderRegistry(
        builders=[],
    )

    service = AffiliateLinkService(
        registry=registry,
    )

    with pytest.raises(
        ValueError,
        match="debe utilizar HTTP o HTTPS",
    ):
        service.build(
            provider_id="future_store",
            product_url="javascript:alert('test')",
        )