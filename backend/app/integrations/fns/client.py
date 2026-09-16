"""Клиент интеграции с ФНС России (СМЭВ / api-fns)."""

import httpx

from app.core.config import get_settings
from app.integrations.base import IntegrationClient, IntegrationError, IntegrationResponse

settings = get_settings()


class FNSClient(IntegrationClient):
    """Клиент API ФНС."""

    def __init__(self) -> None:
        self.api_url = settings.FNS_API_URL
        self.api_key = settings.FNS_API_KEY

    async def send_request(self, payload: dict) -> IntegrationResponse:
        """Запрос выписки ЕГРЮЛ/ЕГРИП по ИНН."""
        if not self.api_key:
            return IntegrationResponse(ok=False, error="FNS_API_KEY is not configured")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.api_url}/api/v1",
                    params={"key": self.api_key, **payload},
                )
            resp.raise_for_status()
            return IntegrationResponse(ok=True, data=resp.json())
        except httpx.HTTPStatusError as exc:
            raise IntegrationError(
                f"ФНС вернула ошибку {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            raise IntegrationError(f"Сетевая ошибка ФНС: {exc}") from exc

    async def get_egrul_by_inn(self, inn: str) -> IntegrationResponse:
        """Выписка ЕГРЮЛ по ИНН юридического лица."""
        return await self.send_request({"req": inn})

    async def get_debtor_info(self, inn: str) -> IntegrationResponse:
        """Сведения о налогоплательщике (ИП) по ИНН."""
        return await self.send_request({"req": inn})