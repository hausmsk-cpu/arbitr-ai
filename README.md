# Arbitr AI

**Financial Unbundled Trustee** — AI-платформа для автоматизации работы финансового управляющего в делах о банкротстве физических лиц.

## Ключевая ценность

- **Сокращение времени** на рутинные операции (запросы, отчёты, документы)
- **Контроль сроков** — ни одного пропущенного дедлайна
- **Полнота данных** — автоматический сбор из госорганов
- **Снижение рисков** — юридическая валидация, аудит, соответствие ФЗ

## Быстрый старт

```bash
# 1. Запуск инфраструктуры (PostgreSQL, Redis, MinIO)
docker compose up -d postgres redis minio

# 2. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
uvicorn app.main:app --reload   # http://localhost:8000/docs

# 3. Frontend
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

## Архитектура

```
[Управляющий] → [Веб-кабинет React] → [API Gateway FastAPI] → [Микросервисы]
                                          ↓
                                [AI-ядро: LLM + RAG] ← [База знаний: законы, шаблоны]
                                          ↓
                        [Модуль запросов] → [ФНС / Росреестр / ФССП / Почта]
                                          ↓
                          [Модуль анализа] → [Реестр / Отчёты / Дашборд]
                                          ↓
                      [Harness CI/CD] → [Dev / Stage / Prod (Kubernetes)]
```

## Структура репозитория

```
Arbitr AI/
├── backend/          # FastAPI + SQLAlchemy + Celery
├── frontend/         # React 18 + TypeScript + Vite + Ant Design
├── integrations/     # адаптеры: ФНС, Росреестр, ФССП, Почта России
├── infra/            # Terraform, Helm, Kubernetes
├── docs/             # архитектура, API, юридическая документация
└── .harness/         # Harness CI/CD: pipelines, environments, secrets, FF
```

## Документация

- [Архитектура](docs/architecture/architecture.md)
- [API](docs/api/openapi.md)
- [Юридические аспекты](docs/legal/legal-compliance.md)
- [Pipeline Harness](.harness/pipelines/)
- [Feature Flags](.harness/feature-flags.yaml)

## Лицензия

Проприетарная. Все права защищены © 2024 Arbitr AI.