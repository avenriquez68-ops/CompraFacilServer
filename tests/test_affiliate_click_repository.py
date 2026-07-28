"""Pruebas del repositorio de clics de afiliados."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import Base
from app.models.affiliate_click import AffiliateClickModel
from app.repositories.affiliate_click import AffiliateClickRepository
from datetime import datetime, timezone


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

def test_repository_counts_clicks_for_provider() -> None:
    """Debe contar únicamente los clics del proveedor solicitado."""

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

    total = repository.count_total(
        session=session,
        provider_id="mercado_libre",
    )

    assert total == 2

    session.close()
    engine.dispose()

def test_repository_lists_recent_clicks_for_provider() -> None:
    """Debe listar clics recientes de un solo proveedor."""

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

    repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://ejemplo.com/producto-3",
        destination_url="https://tienda.com/afiliado-3",
    )

    clicks = repository.list_recent(
        session=session,
        limit=10,
        provider_id="mercado_libre",
    )

    assert len(clicks) == 2
    assert all(
        click.provider_id == "mercado_libre"
        for click in clicks
    )

    session.close()
    engine.dispose()

def test_repository_counts_clicks_in_date_range() -> None:
    """Debe contar clics dentro del rango solicitado."""

    session, engine = create_test_session()
    repository = AffiliateClickRepository()

    first_click = repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://ejemplo.com/producto-1",
        destination_url="https://tienda.com/afiliado-1",
    )
    first_click.created_at = datetime(
        2026,
        7,
        1,
        tzinfo=timezone.utc,
    )

    second_click = repository.create(
        session=session,
        provider_id="amazon",
        product_url="https://ejemplo.com/producto-2",
        destination_url="https://tienda.com/afiliado-2",
    )
    second_click.created_at = datetime(
        2026,
        7,
        15,
        tzinfo=timezone.utc,
    )

    third_click = repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://ejemplo.com/producto-3",
        destination_url="https://tienda.com/afiliado-3",
    )
    third_click.created_at = datetime(
        2026,
        7,
        25,
        tzinfo=timezone.utc,
    )

    session.commit()

    total = repository.count_total(
        session=session,
        date_from=datetime(
            2026,
            7,
            10,
            tzinfo=timezone.utc,
        ),
        date_to=datetime(
            2026,
            7,
            31,
            tzinfo=timezone.utc,
        ),
    )

    assert total == 2

    session.close()
    engine.dispose()

def test_repository_lists_recent_clicks_in_date_range() -> None:
    """Debe listar clics recientes dentro del rango solicitado."""

    session, engine = create_test_session()
    repository = AffiliateClickRepository()

    first_click = repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://ejemplo.com/producto-1",
        destination_url="https://tienda.com/afiliado-1",
    )
    first_click.created_at = datetime(
        2026,
        7,
        1,
        tzinfo=timezone.utc,
    )

    second_click = repository.create(
        session=session,
        provider_id="amazon",
        product_url="https://ejemplo.com/producto-2",
        destination_url="https://tienda.com/afiliado-2",
    )
    second_click.created_at = datetime(
        2026,
        7,
        15,
        tzinfo=timezone.utc,
    )

    third_click = repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://ejemplo.com/producto-3",
        destination_url="https://tienda.com/afiliado-3",
    )
    third_click.created_at = datetime(
        2026,
        7,
        25,
        tzinfo=timezone.utc,
    )

    session.commit()

    clicks = repository.list_recent(
        session=session,
        limit=10,
        date_from=datetime(
            2026,
            7,
            10,
            tzinfo=timezone.utc,
        ),
        date_to=datetime(
            2026,
            7,
            20,
            tzinfo=timezone.utc,
        ),
    )

    assert len(clicks) == 1
    assert clicks[0].id == second_click.id
    assert clicks[0].provider_id == "amazon"

    session.close()
    engine.dispose()

def test_repository_counts_by_provider_in_date_range() -> None:
    """Debe agrupar solamente los clics dentro del rango."""

    session, engine = create_test_session()
    repository = AffiliateClickRepository()

    first_click = repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://ejemplo.com/producto-1",
        destination_url="https://tienda.com/afiliado-1",
    )
    first_click.created_at = datetime(
        2026,
        7,
        1,
        tzinfo=timezone.utc,
    )

    second_click = repository.create(
        session=session,
        provider_id="amazon",
        product_url="https://ejemplo.com/producto-2",
        destination_url="https://tienda.com/afiliado-2",
    )
    second_click.created_at = datetime(
        2026,
        7,
        15,
        tzinfo=timezone.utc,
    )

    third_click = repository.create(
        session=session,
        provider_id="mercado_libre",
        product_url="https://ejemplo.com/producto-3",
        destination_url="https://tienda.com/afiliado-3",
    )
    third_click.created_at = datetime(
        2026,
        7,
        25,
        tzinfo=timezone.utc,
    )

    session.commit()

    totals = repository.count_by_provider(
        session=session,
        date_from=datetime(
            2026,
            7,
            10,
            tzinfo=timezone.utc,
        ),
        date_to=datetime(
            2026,
            7,
            31,
            tzinfo=timezone.utc,
        ),
    )

    assert totals == {
        "amazon": 1,
        "mercado_libre": 1,
    }

    session.close()
    engine.dispose()