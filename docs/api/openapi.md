# API Arbitr AI — Спецификация

База: `http://localhost:8000` · Swagger: `/docs`

Аутентификация: `Authorization: Bearer <JWT>`

## Здоровье сервиса

### `GET /health`

```json
{ "status": "ok", "app": "Arbitr AI", "version": "0.1.0" }
```

## Аутентификация

### `POST /api/v1/auth/register`

| Поле | Тип | Описание |
|------|-----|----------|
| email | string | Email пользователя |
| password | string | Пароль (мин. 8 симв.) |
| full_name | string | ФИО |

### `POST /api/v1/auth/login`

→ `{ "access_token": "...", "token_type": "bearer", "expires_in": 3600 }`

### `GET /api/v1/auth/me` (авторизованный)

→ данные текущего пользователя

## Дела о банкротстве

### `GET /api/v1/cases` — список дел управляющего

### `POST /api/v1/cases` — создать дело

```json
{
  "case_number": "А41-12345/2024",
  "court_name": "Арбитражный суд Московской области",
  "court_region": "Московская область",
  "procedure_type": "bankruptcy"
}
```

### `GET /api/v1/cases/{id}` — детали дела

### `PATCH /api/v1/cases/{id}` — обновить дело

### `DELETE /api/v1/cases/{id}` — удалить дело

## Подмодели дела

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET/POST | `/api/v1/cases/{id}/debtors` | должники |
| GET/POST | `/api/v1/cases/{id}/creditors` | кредиторы |
| GET/POST | `/api/v1/cases/{id}/properties` | имущество |
| GET | `/api/v1/cases/{id}/documents` | документы |

## Запросы в госорганы

### `GET /api/v1/requests?case_id={id}` — список запросов

### `POST /api/v1/requests?case_id={id}` — создать запрос

```json
{
  "request_type": "fns",
  "title": "Выписка о счетах должника",
  "target_org": "ФНС №14",
  "content": "Прошу предоставить...",
  "sending_method": "api"
}
```

### `PATCH /api/v1/requests/{id}` — обновить статус

```json
{ "status": "sent", "external_tracking": "RA123456789RU" }
```

## Коды ошибок

| Код | Значение |
|-----|----------|
| 400 | Некорректный запрос |
| 401 | Не авторизован |
| 403 | Нет прав |
| 404 | Не найдено |
| 409 | Конфликт (email занят) |
| 422 | Ошибка валидации |