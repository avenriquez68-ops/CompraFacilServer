"""Esquemas públicos para clics de afiliados."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AffiliateClickItem(BaseModel):
    """Clic de afiliado que puede devolverse mediante la API."""

    id: int
    provider_id: str
    product_url: str
    destination_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AffiliateClickStatsResponse(BaseModel):
    """Resumen de las estadísticas de clics."""

    total_clicks: int = Field(ge=0)
    clicks_by_provider: dict[str, int]
    recent_clicks: list[AffiliateClickItem]