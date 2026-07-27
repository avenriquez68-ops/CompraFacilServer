"""Pruebas del repositorio de clics de afiliados."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import Base
from app.models.affiliate_click import AffiliateClickModel
from app.repositories.affiliate_click import AffiliateClickRepository


def create_test_session() -> tuple[Session, object]:
    """Crea una base de datos temporal en memoria."""

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    return Session(engine), engine


def test_repository_saves_affiliate_click() -> None:
    """El repositorio debe guardar un clic de afiliado."""

    session, engine = create_test_session()
    repository = AffiliateClickRepository()

    saved_click = repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://www.mercadolibre.com.mx/producto",
        destination_url="https://www.mercadolibre.com.mx/producto",
    )

    assert saved_click.id is not None
    assert saved_click.provider_id == "mercado_libre"
    assert (
        saved_click.product_url
        == "https://www.mercadolibre.com.mx/producto"
    )
    assert (
        saved_click.destination_url
        == "https://www.mercadolibre.com.mx/producto"
    )
    assert saved_click.created_at is not None

    session.close()
    engine.dispose()

def test_repository_lists_newest_click_first() -> None:
    """Debe devolver primero el clic más reciente."""

    session, engine = create_test_session()
    repository = AffiliateClickRepository()

    repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://ejemplo.com/producto-1",
        destination_url="https://tienda.com/afiliado-1",
    )

    repository.create(
        session=session,
        provider_id="amazon",
        product_url="https://ejemplo.com/producto-2",
        destination_url="https://tienda.com/afiliado-2",
    )

    clicks = repository.list_recent(
        session=session,
        limit=10,
    )

    assert len(clicks) == 2
    assert isinstance(clicks[0], AffiliateClickModel)
    assert clicks[0].provider_id == "amazon"
    assert clicks[1].provider_id == "mercado_libre"

    session.close()
    engine.dispose()

def test_repository_counts_total_clicks() -> None:
    """Debe devolver el número total de clics."""

    session, engine = create_test_session()
    repository = AffiliateClickRepository()

    repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://ejemplo.com/producto-1",
        destination_url="https://tienda.com/afiliado-1",
    )

    repository.create(
        session=session,
        provider_id="amazon",
        product_url="https://ejemplo.com/producto-2",
        destination_url="https://tienda.com/afiliado-2",
    )

    total = repository.count_total(session=session)

    assert total == 2

    session.close()
    engine.dispose()

def test_repository_counts_clicks_by_provider() -> None:
    """Debe agrupar el número de clics por proveedor."""

    session, engine = create_test_session()
    repository = AffiliateClickRepository()

    repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://ejemplo.com/producto-1",
        destination_url="https://tienda.com/afiliado-1",
    )

    repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://ejemplo.com/producto-2",
        destination_url="https://tienda.com/afiliado-2",
    )

    repository.create(
        session=session,
        provider_id="amazon",
        product_url="https://ejemplo.com/producto-3",
        destination_url="https://tienda.com/afiliado-3",
    )

    totals = repository.count_by_provider(
        session=session,
    )

    assert totals == {
        "amazon": 1,
        "mercado_libre": 2,
    }

    session.close()
    engine.dispose()