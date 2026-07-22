"""Cliente HTTP para consultar Mercado Libre."""

from typing import Any

import httpx

from app.core.config import Settings, settings
from app.infrastructure.clients.exceptions import ExternalStoreError
from app.schemas.product import Product


class MercadoLibreClient:
    """Consulta y normaliza productos de Mercado Libre México."""

    def __init__(
        self,
        app_settings: Settings = settings,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = app_settings
        self._http_client = http_client

    async def search_products(
        self,
        query: str,
        limit: int = 20,
    ) -> list[Product]:
        """Busca productos y los convierte al formato de Compra Fácil."""

        endpoint = (
            f"{self._settings.mercado_libre_base_url}"
            f"/sites/{self._settings.mercado_libre_site_id}/search"
        )

        headers = {
            "Accept": "application/json",
            "User-Agent": "CompraFacilServer/0.3",
        }

        token = self._settings.mercado_libre_access_token.strip()

        if token:
            headers["Authorization"] = f"Bearer {token}"

        params = {
            "q": query,
            "limit": limit,
        }

        try:
            if self._http_client is not None:
                response = await self._http_client.get(
                    endpoint,
                    params=params,
                    headers=headers,
                )
            else:
                async with httpx.AsyncClient(
                    timeout=self._settings.mercado_libre_timeout_seconds
                ) as client:
                    response = await client.get(
                        endpoint,
                        params=params,
                        headers=headers,
                    )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise ExternalStoreError(
                "Mercado Libre tardó demasiado en responder."
            ) from exc

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            if status_code in {401, 403}:
                message = (
                    "Mercado Libre rechazó la consulta. "
                    "Puede ser necesario configurar un token de acceso."
                )
            else:
                message = (
                    "Mercado Libre respondió con el código "
                    f"{status_code}."
                )

            raise ExternalStoreError(message) from exc

        except httpx.RequestError as exc:
            raise ExternalStoreError(
                "No fue posible establecer comunicación con Mercado Libre."
            ) from exc

        data = response.json()
        raw_results = data.get("results", [])

        return [
            self._normalize_product(item)
            for item in raw_results
            if item.get("id")
            and item.get("title")
            and item.get("permalink")
            and item.get("price") is not None
        ]

    @staticmethod
    def _normalize_product(item: dict[str, Any]) -> Product:
        """Convierte un producto externo al esquema interno."""

        shipping = item.get("shipping") or {}

        seller = item.get("seller") or {}
        seller_name = (
            seller.get("nickname")
            or seller.get("id")
            or "Mercado Libre"
        )

        return Product(
            id=str(item["id"]),
            nombre=str(item["title"]),
            precio=float(item["price"]),
            precio_original=(
                float(item["original_price"])
                if item.get("original_price") is not None
                else None
            ),
            moneda=str(item.get("currency_id", "MXN")),
            tienda=f"Mercado Libre · {seller_name}",
            url=item["permalink"],
            imagen_url=item.get("thumbnail"),
            condicion=item.get("condition"),
            envio_gratis=bool(shipping.get("free_shipping", False)),
            calificacion=None,
            numero_resenas=0,
        )


mercado_libre_client = MercadoLibreClient()