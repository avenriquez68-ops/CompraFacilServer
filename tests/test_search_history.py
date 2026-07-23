"""Pruebas del repositorio del historial de búsquedas."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import Base
from app.models.search_history import SearchHistoryModel
from app.repositories.search_history import SearchHistoryRepository
from app.schemas.product import SearchResponse


def create_test_session() -> tuple[Session, object]:
    """Crea una base de datos temporal en memoria."""

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    return Session(engine), engine


def test_repository_saves_search() -> None:
    """El repositorio debe guardar una búsqueda."""

    session, engine = create_test_session()
    repository = SearchHistoryRepository()

    search_result = SearchResponse(
        query="laptop",
        total=3,
        source="mercado_libre",
        fallback_used=False,
        warning=None,
        products=[],
    )

    saved_item = repository.create(
        session=session,
        search_result=search_result,
    )

    assert saved_item.id is not None
    assert saved_item.query == "laptop"
    assert saved_item.total_results == 3
    assert saved_item.source == "mercado_libre"
    assert saved_item.fallback_used is False

    session.close()
    engine.dispose()


def test_repository_lists_newest_search_first() -> None:
    """El historial debe devolver primero el registro más reciente."""

    session, engine = create_test_session()
    repository = SearchHistoryRepository()

    first_result = SearchResponse(
        query="laptop",
        total=2,
        source="simulated_fallback",
        fallback_used=True,
        warning="Prueba",
        products=[],
    )

    second_result = SearchResponse(
        query="celular",
        total=5,
        source="mercado_libre",
        fallback_used=False,
        warning=None,
        products=[],
    )

    repository.create(
        session=session,
        search_result=first_result,
    )

    repository.create(
        session=session,
        search_result=second_result,
    )

    history = repository.list_recent(
        session=session,
        limit=10,
    )

    assert len(history) == 2
    assert isinstance(history[0], SearchHistoryModel)
    assert history[0].query == "celular"
    assert history[1].query == "laptop"

    session.close()
    engine.dispose()