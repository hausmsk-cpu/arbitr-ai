"""Адаптеры интеграций с госорганами."""

from app.integrations.base import IntegrationClient, IntegrationError, IntegrationResponse

__all__ = ["IntegrationClient", "IntegrationError", "IntegrationResponse"]