"""База клиентов интеграций."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class IntegrationError(Exception):
    """Ошибка интеграции с внешним сервисом."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class IntegrationResponse:
    """Ответ внешнего сервиса."""

    ok: bool
    data: dict | None = None
    raw: str | None = None
    error: str | None = None
    extra: dict = field(default_factory=dict)


class IntegrationClient(ABC):
    """Абстрактный клиент интеграции."""

    @abstractmethod
    async def send_request(self, payload: dict) -> IntegrationResponse:
        """Отправка запроса в орган."""
        raise NotImplementedError