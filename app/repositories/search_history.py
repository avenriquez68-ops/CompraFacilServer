"""Operaciones de base de datos para el historial."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.search_history import SearchHistoryModel
from app.schemas.product import SearchResponse


class SearchHistoryRepository:
    """Guarda y consulta búsquedas realizadas."""

    def create(
        self,
        session: Session,
        search_result: SearchResponse,
    ) -> SearchHistoryModel:
        """Guarda una búsqueda y devuelve el registro creado."""

        history_item = SearchHistoryModel(
            query=search_result.query,
            total_results=search_result.total,
            source=search_result.source,
            fallback_used=search_result.fallback_used,
        )

        session.add(history_item)
        session.commit()
        session.refresh(history_item)

        return history_item

    def list_recent(
        self,
        session: Session,
        limit: int = 20,
    ) -> list[SearchHistoryModel]:
        """Devuelve las búsquedas más recientes."""

        statement = (
            select(SearchHistoryModel)
            .order_by(SearchHistoryModel.created_at.desc())
            .limit(limit)
        )

        return list(session.scalars(statement).all())

    def delete_all(self, session: Session) -> int:
        """Elimina todo el historial y devuelve el total eliminado."""

        history_items = self.list_recent(
            session=session,
            limit=10_000,
        )

        total_deleted = len(history_items)

        for item in history_items:
            session.delete(item)

        session.commit()

        return total_deleted


search_history_repository = SearchHistoryRepository()