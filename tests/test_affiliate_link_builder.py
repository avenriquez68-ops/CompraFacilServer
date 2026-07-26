"""Pruebas para los generadores de enlaces de afiliado."""

import pytest

from app.affiliates.base import PassthroughAffiliateLinkBuilder


def test_builder_normalizes_provider_id() -> None:
    """El identificador debe eliminar espacios y convertirse a minúsculas."""

    builder = PassthroughAffiliateLinkBuilder(
        provider_id="  Mercado_Libre  "
    )

    assert builder.provider_id == "mercado_libre"


def test_builder_returns_original_https_url() -> None:
    """Una URL HTTPS válida debe devolverse sin modificaciones."""

    builder = PassthroughAffiliateLinkBuilder(
        provider_id="mercado_libre"
    )

    product_url = (
        "https://www.mercadolibre.com.mx/producto-ejemplo"
    )

    result = builder.build(product_url)

    assert result == product_url


def test_builder_returns_original_http_url() -> None:
    """Una URL HTTP válida debe devolverse sin modificaciones."""

    builder = PassthroughAffiliateLinkBuilder(
        provider_id="demo_store"
    )

    product_url = "http://example.com/producto/123"

    result = builder.build(product_url)

    assert result == product_url


def test_builder_removes_url_surrounding_spaces() -> None:
    """La URL debe normalizar los espacios exteriores."""

    builder = PassthroughAffiliateLinkBuilder(
        provider_id="demo_store"
    )

    result = builder.build(
        "  https://example.com/producto/123  "
    )

    assert result == "https://example.com/producto/123"


def test_builder_rejects_empty_provider_id() -> None:
    """No debe permitirse un identificador de proveedor vacío."""

    with pytest.raises(
        ValueError,
        match="El identificador del proveedor es obligatorio",
    ):
        PassthroughAffiliateLinkBuilder(provider_id="   ")


def test_builder_rejects_empty_product_url() -> None:
    """No debe permitirse una URL vacía."""

    builder = PassthroughAffiliateLinkBuilder(
        provider_id="mercado_libre"
    )

    with pytest.raises(
        ValueError,
        match="La URL del producto es obligatoria",
    ):
        builder.build("   ")


@pytest.mark.parametrize(
    "invalid_url",
    [
        "www.example.com/producto/123",
        "ftp://example.com/producto/123",
        "javascript:alert('prueba')",
    ],
)
def test_builder_rejects_unsupported_url_scheme(
    invalid_url: str,
) -> None:
    """Solo deben permitirse direcciones HTTP y HTTPS."""

    builder = PassthroughAffiliateLinkBuilder(
        provider_id="mercado_libre"
    )

    with pytest.raises(
        ValueError,
        match="debe utilizar HTTP o HTTPS",
    ):
        builder.build(invalid_url)


@pytest.mark.parametrize(
    "invalid_url",
    [
        "https://",
        "http://",
    ],
)
def test_builder_rejects_url_without_domain(
    invalid_url: str,
) -> None:
    """La URL debe contener un dominio."""

    builder = PassthroughAffiliateLinkBuilder(
        provider_id="mercado_libre"
    )

    with pytest.raises(
        ValueError,
        match="debe contener un dominio válido",
    ):
        builder.build(invalid_url)