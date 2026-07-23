"""Pruebas para los metadatos de búsqueda."""

from app.schemas.product import SearchResponse
from app.schemas.search_metadata import SearchMetadata


def test_search_metadata_defaults() -> None:
    """Los campos de listas deben iniciar vacíos."""

    metadata = SearchMetadata(
        source="multi_provider",
    )

    assert metadata.source == "multi_provider"
    assert metadata.fallback_used is False
    assert metadata.stores_consulted == []
    assert metadata.stores_succeeded == []
    assert metadata.stores_failed == []
    assert metadata.warnings == []


def test_search_response_accepts_metadata() -> None:
    """SearchResponse debe aceptar metadatos técnicos."""

    metadata = SearchMetadata(
        source="multi_provider",
        fallback_used=False,
        stores_consulted=["Mercado Libre"],
        stores_succeeded=["Mercado Libre"],
        stores_failed=[],
        warnings=[],
    )

    response = SearchResponse(
        query="laptop",
        total=0,
        source="mercado_libre",
        fallback_used=False,
        products=[],
        metadata=metadata,
    )

    assert response.metadata is not None
    assert response.metadata.source == "multi_provider"

    assert response.metadata.stores_consulted == [
        "Mercado Libre"
    ]

    assert response.metadata.stores_succeeded == [
        "Mercado Libre"
    ]