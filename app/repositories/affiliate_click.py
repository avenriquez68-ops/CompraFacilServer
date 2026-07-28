"""Operaciones de base de datos para clics de afiliados."""

from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.affiliate_click import AffiliateClickModel


class AffiliateClickRepository:
    """Guarda los clics realizados en enlaces afiliados."""

    def create(
        self,
        session: Session,
        provider_id: str,
        product_url: str,
        destination_url: str,
    ) -> AffiliateClickModel:
        """Guarda un clic y devuelve el registro creado."""

        click = AffiliateClickModel(
            provider_id=provider_id,
            product_url=product_url,
            destination_url=destination_url,
        )

        session.add(click)
        session.commit()
        session.refresh(click)

        return click

    def list_recent(
        self,
        session: Session,
        limit: int = 20,
        provider_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[AffiliateClickModel]:
        """Devuelve los clics más recientes."""

        statement = select(AffiliateClickModel)

        if provider_id is not None:
            statement = statement.where(
                AffiliateClickModel.provider_id == provider_id
            )

        if date_from is not None:
            statement = statement.where(
                AffiliateClickModel.created_at >= date_from
            )

        if date_to is not None:
            statement = statement.where(
                AffiliateClickModel.created_at <= date_to
            )

        statement = (
            statement
            .order_by(
                AffiliateClickModel.created_at.desc(),
                AffiliateClickModel.id.desc(),
            )
            .limit(limit)
        )

        return list(session.scalars(statement).all())

    def count_total(
        self,
        session: Session,
        provider_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> int:
        """Devuelve el número total de clics registrados."""

        statement = select(
            func.count(AffiliateClickModel.id)
        )

        if provider_id is not None:
            statement = statement.where(
                AffiliateClickModel.provider_id == provider_id
            )

        if date_from is not None:
            statement = statement.where(
                AffiliateClickModel.created_at >= date_from
            )

        if date_to is not None:
            statement = statement.where(
                AffiliateClickModel.created_at <= date_to
            )

        total = session.scalar(statement)

        return int(total or 0)

    def count_by_provider(
        self,
        session: Session,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict[str, int]:
        """Devuelve el número de clics agrupado por proveedor."""

        statement = select(
            AffiliateClickModel.provider_id,
            func.count(AffiliateClickModel.id),
        )

        if date_from is not None:
            statement = statement.where(
                AffiliateClickModel.created_at >= date_from
            )

        if date_to is not None:
            statement = statement.where(
                AffiliateClickModel.created_at <= date_to
            )

        statement = (
            statement
            .group_by(AffiliateClickModel.provider_id)
            .order_by(AffiliateClickModel.provider_id)
        )

        rows = session.execute(statement).all()

        return {
            provider_id: int(total)
            for provider_id, total in rows
        }

affiliate_click_repository = AffiliateClickRepository()