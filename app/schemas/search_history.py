"""Esquemas públicos del historial de búsquedas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SearchHistoryItem(BaseModel):
    """Búsqueda guardada que puede devolverse mediante la API."""

    id: int
    query: str
    total_results: int = Field(ge=0)
    source: str
    fallback_used: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)