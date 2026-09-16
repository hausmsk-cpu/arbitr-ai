# ArbitrAI Backend

AI-платформа для автоматизации работы финансового управляющего в делах о банкротстве физических лиц.

## Запуск локально

```bash
# Виртуальное окружение
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e ".[dev]"

# Миграции
alembic upgrade head

# Сервер
uvicorn app.main:app --reload
```

## Тесты

```bash
pytest -v --cov=app
```

## Структура

```
app/
├── api/           # FastAPI-роутеры
├── core/          # конфигурация, БД, безопасность
├── models/        # SQLAlchemy-модели
├── schemas/       # Pydantic-схемы
├── services/      # бизнес-логика
├── integrations/  # ФНС, Росреестр, ФССП, Почта России
├── ai/            # генерация документов, RAG
└── tasks/         # Celery-задачи
```