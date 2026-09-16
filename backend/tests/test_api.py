"""Тесты API: health-check, аутентификация, CRUD дел.

Примечание: работают на SQLite (см. conftest.py).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["app"] == "Arbitr AI"


@pytest.mark.asyncio
async def test_cases_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/cases")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_requests_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/requests")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_register_validation(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "bad-email", "password": "short", "full_name": ""},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient) -> None:
    """Полный цикл: регистрация → вход → доступ к делам."""
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "manager@test.ru", "password": "secret-pass-1", "full_name": "Иван Иванов"},
    )
    assert register.status_code == 201, register.text

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "manager@test.ru", "password": "secret-pass-1"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    assert token

    cases = await client.get(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cases.status_code == 200
    assert cases.json() == []


@pytest.mark.asyncio
async def test_case_crud_flow(client: AsyncClient) -> None:
    """Создание дела, добавление должника, просмотр."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "crud@test.ru", "password": "secret-pass-2", "full_name": "Тест CRUD"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "crud@test.ru", "password": "secret-pass-2"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создание дела
    create = await client.post(
        "/api/v1/cases",
        json={
            "case_number": "А32-37431/2025",
            "court_name": "Арбитражный суд Краснодарского края",
            "court_region": "Краснодарский край",
            "procedure_type": "bankruptcy",
        },
        headers=headers,
    )
    assert create.status_code == 201, create.text
    case = create.json()
    case_id = case["id"]
    assert case["case_number"] == "А32-37431/2025"

    # Добавление должника
    debtor = await client.post(
        f"/api/v1/cases/{case_id}/debtors",
        json={"full_name": "Макурин Василий Викторович", "inn": "235300580821"},
        headers=headers,
    )
    assert debtor.status_code == 201, debtor.text
    assert debtor.json()["inn"] == "235300580821"

    # Список дел
    cases = await client.get("/api/v1/cases", headers=headers)
    assert len(cases.json()) == 1

    # Удаление дела
    delete = await client.delete(f"/api/v1/cases/{case_id}", headers=headers)
    assert delete.status_code == 204