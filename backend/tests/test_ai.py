"""Тесты AI-модуля: генерация документов и RAG-поиск.

Работают на SQLite (см. conftest.py).
"""

import pytest
from httpx import AsyncClient


async def _get_token(client: AsyncClient) -> str:
    """Регистрирует тестового пользователя и возвращает JWT."""
    email = "test-ai@arbitr.ai"
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "test-pass-123", "full_name": "Тест ИИ"},
    )
    assert resp.status_code == 201, resp.text

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "test-pass-123"},
    )
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


AI_PAYLOAD = {
    "doc_type": "request_fns",
    "case_number": "А32-37431/2025",
    "court_name": "Арбитражный суд Краснодарского края",
    "court_decision_date": "27.08.2025",
    "kad_url": "https://kad.arbitr.ru/Card/test",
    "debtor_full_name": "Макурин Василий Викторович",
    "debtor_birth_date": "18.02.1955",
    "debtor_birth_place": "гор. Баку Азербайджан",
    "debtor_inn": "235300580821",
    "debtor_snils": "130-262-377 12",
    "debtor_address": "Краснодарский край, Тимашевский район, г. Тимашевск, СОТ «Строитель»",
    "spouse_full_name": "Макурина Светлана Аркадьевна",
    "spouse_birth_date": "01.04.1957",
    "spouse_birth_place": "гор. Омск",
    "manager_full_name": "Павленко Марина Леонидовна",
    "manager_address": "352708, г. Тимашевск, ул. Ленина д.89, а/я 186",
    "manager_email": "arbitr-pavlenko@yandex.ru",
    "manager_phone": "8-905-405-12-50",
    "manager_snils": "125-612-580 39",
    "period_start": "07.07.2015",
}


@pytest.mark.asyncio
async def test_ai_types_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/ai/types")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ai_document_types(client: AsyncClient) -> None:
    token = await _get_token(client)
    resp = await client.get(
        "/api/v1/ai/types",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    types = resp.json()
    assert "request_fns" in types
    assert "request_spouse" in types
    assert len(types) >= 20


@pytest.mark.asyncio
async def test_ai_generate_request_fns(client: AsyncClient) -> None:
    token = await _get_token(client)
    resp = await client.post(
        "/api/v1/ai/generate",
        json=AI_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    text = data["text"]

    # Проверяем ключевые блоки запроса в ФНС
    assert "ЗАПРОС" in text
    assert "Макурин Василий Викторович" in text
    assert "ИНН: 235300580821" in text
    assert "2-НДФЛ" in text
    assert "213.25" in text
    assert "П Р О Ш У" in text
    assert "Финансовый управляющий Павленко Марина Леонидовна" in text
    assert data["doc_type_name"] == "Запрос в ФНС России"


@pytest.mark.asyncio
async def test_ai_generate_request_spouse(client: AsyncClient) -> None:
    """Генерация требования к супругу — особый сценарий кейса."""
    token = await _get_token(client)
    payload = dict(AI_PAYLOAD, doc_type="request_spouse")
    resp = await client.post(
        "/api/v1/ai/generate",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    text = resp.json()["text"]
    assert "Т Р Е Б У Ю" in text
    assert "совместно нажитого имущества" in text
    assert "Макурина Светлана Аркадьевна" in text


@pytest.mark.asyncio
async def test_ai_generate_completion_petition(client: AsyncClient) -> None:
    """Ходатайство о завершении — включает сценарий смерти должника."""
    token = await _get_token(client)
    payload = dict(AI_PAYLOAD, doc_type="completion_petition")
    resp = await client.post(
        "/api/v1/ai/generate",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    text = resp.json()["text"]
    assert "ХОДАТАЙСТВО" in text
    assert "параграфа 4 главы X" in text
    assert "освободить" in text


@pytest.mark.asyncio
async def test_ai_generate_unknown_type(client: AsyncClient) -> None:
    token = await _get_token(client)
    payload = dict(AI_PAYLOAD, doc_type="nonexistent")
    resp = await client.post(
        "/api/v1/ai/generate",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_ai_rag_search(client: AsyncClient) -> None:
    token = await _get_token(client)
    resp = await client.get(
        "/api/v1/ai/search",
        params={"q": "смерть должника наследники нотариус"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    first = data["results"][0]
    assert "source" in first
    assert "text" in first


@pytest.mark.asyncio
async def test_ai_stats(client: AsyncClient) -> None:
    token = await _get_token(client)
    resp = await client.get(
        "/api/v1/ai/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    stats = resp.json()
    assert stats["chunks"] > 100
    assert stats["terms"] > 500