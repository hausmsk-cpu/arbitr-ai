"""Клиент интеграции с ФССП (банк данных исполнительных производств)."""

import httpx

from app.core.config import get_settings
from app.integrations.base import IntegrationClient, IntegrationError, IntegrationResponse

settings = get_settings()


class FSSPClient(IntegrationClient):
    """Клиент открытого банка данных ФССП."""

    def __init__(self) -> None:
        self.api_url = settings.FSSP_API_URL or "https://api-ip.fssp.gov.ru/api/v1.0"

    async def send_request(self, payload: dict) -> IntegrationResponse:
        """Поиск исполнительных производств по физическому лицу."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(f"{self.api_url}/search/physical", json=payload)
            resp.raise_for_status()
            return IntegrationResponse(ok=True, data=resp.json())
        except httpx.HTTPStatusError as exc:
            raise IntegrationError(
                f"ФССП вернула ошибку {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            raise IntegrationError(f"Сетевая ошибка ФССП: {exc}") from exc

    async def search_physical(
        self,
        region: str,
        first_name: str,
        last_name: str,
        second_name: str | None = None,
        birth_date: str | None = None,
    ) -> IntegrationResponse:
        """Поиск производств по ФИО и региону."""
        payload = {
            "region": region,
            "firstname": first_name,
            "lastname": last_name,
        }
        if second_name:
            payload["secondname"] = second_name
        if birth_date:
            payload["birthdate"] = birth_date
        return await self.send_request(payload)