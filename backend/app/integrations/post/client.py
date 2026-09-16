"""Клиент API Почты России (электронные заказные письма)."""

import httpx

from app.core.config import get_settings
from app.integrations.base import IntegrationClient, IntegrationError, IntegrationResponse

settings = get_settings()


class PostClient(IntegrationClient):
    """Клиент API Почты России: чистые и электронные заказные письма."""

    def __init__(self) -> None:
        self.api_url = settings.POST_API_URL
        self.token = settings.POST_API_TOKEN

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"AccessToken {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json;charset=UTF-8",
        }

    async def send_request(self, payload: dict) -> IntegrationResponse:
        """Создание электронного заказного письма."""
        if not self.token:
            return IntegrationResponse(ok=False, error="POST_API_TOKEN is not configured")

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{self.api_url}/v2/orders/easy",
                    json=payload,
                    headers=self._headers(),
                )
            resp.raise_for_status()
            return IntegrationResponse(ok=True, data=resp.json())
        except httpx.HTTPStatusError as exc:
            raise IntegrationError(
                f"Почта России вернула ошибку {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            raise IntegrationError(f"Сетевая ошибка Почты России: {exc}") from exc

    async def send_registered_letter(
        self,
        address: str,
        index: str,
        recipient: str,
        content: str,
    ) -> IntegrationResponse:
        """Электронное заказное письмо (hybrid mail)."""
        payload = {
            "fio": recipient,
            "address": {
                "index": index,
                "region": "",
                "place": "",
                "address": address,
            },
            "letter": {
                "name": "Заказное письмо Arbitr AI",
                "format": "A4",
                "type": "letter",
                "delivery": "simple",
            },
            "content": content,
        }
        return await self.send_request(payload)