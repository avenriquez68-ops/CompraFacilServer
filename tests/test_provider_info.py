"""Pruebas para la información descriptiva de proveedores."""

import pytest
from pydantic import ValidationError

from app.schemas.provider_info import ProviderInfo, ProviderType


def test_provider_info_accepts_valid_data() -> None:
    """El esquema debe aceptar información válida."""

    provider = ProviderInfo(
        provider_id="mercado_libre",
        display_name="Mercado Libre",
        provider_type=ProviderType.MARKETPLACE,
        country_code="MX",
        supports_free_shipping=True,
        supports_ratings=True,
        is_demo=False,
    )

    assert provider.provider_id == "mercado_libre"
    assert provider.display_name == "Mercado Libre"
    assert provider.provider_type == ProviderType.MARKETPLACE
    assert provider.country_code == "MX"
    assert provider.supports_free_shipping is True
    assert provider.supports_ratings is True
    assert provider.is_demo is False


def test_provider_info_rejects_invalid_country_code() -> None:
    """El código del país debe contener exactamente dos caracteres."""

    with pytest.raises(ValidationError):
        ProviderInfo(
            provider_id="invalid_provider",
            display_name="Proveedor inválido",
            provider_type=ProviderType.RETAILER,
            country_code="MEX",
            supports_free_shipping=False,
            supports_ratings=False,
            is_demo=False,
        )


def test_provider_type_serializes_as_string() -> None:
    """El tipo de proveedor debe serializarse como texto."""

    provider = ProviderInfo(
        provider_id="demo_store",
        display_name="Tienda Demo",
        provider_type=ProviderType.DEMO,
        country_code="MX",
        supports_free_shipping=True,
        supports_ratings=True,
        is_demo=True,
    )

    serialized = provider.model_dump(mode="json")

    assert serialized["provider_type"] == "demo"