"""Клиент интеграции с Росреестром.

Росреестр не предоставляет открытого REST API для выписок в реальном времени
(данные доступны через портал, платные сервисы и СМЭВ). Здесь реализован
каркас: та же структура, что у ФНС, но с вызовом через СМЭВ-шлюз или RPA-модуль.
"""

from app.integrations.base import IntegrationClient, IntegrationError, IntegrationResponse
from app.core.config import get_settings

settings = get_settings()


class RosreestrClient(IntegrationClient):
    """Клиент Росреестра (выписка из ЕГРН)."""

    def __init__(self) -> None:
        self.api_url = settings.ROSREESTR_API_URL
        self.api_key = settings.ROSREESTR_API_KEY

    async def send_request(self, payload: dict) -> IntegrationResponse:
        if not self.api_url:
            return IntegrationResponse(ok=False, error="ROSREESTR_API_URL is not configured")

        # TODO: реализация вызова через СМЭВ-шлюз или официальное API.
        raise IntegrationError("Росреестр: вызов через СМЭВ ещё не реализован")

    async def get_egrn_extract(self, cadastral_number: str) -> IntegrationResponse:
        """Выписка из ЕГРН по кадастровому номеру."""
        return await self.send_request({"cadastral_number": cadastral_number})