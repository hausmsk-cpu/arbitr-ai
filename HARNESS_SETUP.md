# Arbitr AI — Настройка Harness CI/CD

> **Аккаунт создан 16.09.2026:**
> - Account Name: `arbitr-ai`
> - Account Id: `17FsggPIQ1yKj5XqvB4zBQ`
> - Harness Cluster: `prod-1`
> - Организация/проект: создаются автоматически через
>   [`infra/harness-terraform/main.tf`](infra/harness-terraform/main.tf)

Пошаговая инструкция подключения проекта **Arbitr AI** (платформа AI-автоматизации
финансового управляющего) к Harness: аккаунт → организация → проект → Git →
секреты → Kubernetes-кластер → деплой.

> Все YAML-конфиги уже подготовлены в папке [`.harness/`](.harness):
> 6 пайплайнов, 3 окружения (dev/stage/prod), 5 feature flags, справочник секретов.
> Осталось только создать ресурсы в UI Harness и скопировать конфиги.

---

## 1. Аккаунт Harness и организация «Arbitr AI»

1. Зарегистрируйтесь на <https://app.harness.io> (можно через GitHub/Google).
2. При первом входе Harness предложит создать **организацию** (Organization):
   - **Имя организации:** `Arbitr AI`
   - **Идентификатор (identifier):** `arbitr-ai` — он уже используется в наших YAML
     как `orgIdentifier: arbitr-ai`.
3. Внутри организации создайте **проект** (Project):
   - **Имя:** `Arbitr AI Platform`
   - **Идентификатор:** `arbitr-ai-platform` (запишите — он пригодится для пайплайнов).
4. Включите модули:
   - **CI** (сборка и тесты),
   - **CD** (деплой в Kubernetes),
   - **Feature Flags** (поэтапное включение функций),
   - **Secrets Management** (встроен).


## 1b. API-ключ для автоматизации (Terraform)

Для создания организации/проекта/секретов автоматически нужен API-токен:

1. В Harness: **Account Settings (верхний правый угол) → Access Control → API Keys**.
2. **Create API Key** → Name: `arbitr-ai-terraform`.
3. **Add Token** → скопируйте токен (показывается один раз).
4. Примените Terraform (см. [`infra/harness-terraform`](infra/harness-terraform)):

   ```bash
   cd infra/harness-terraform
   export HARNESS_PLATFORM_API_KEY="<токен>"
   terraform init && terraform plan && terraform apply
   ```

> Токен sensitive — храните в менеджере паролей, не коммитьте.

------

## 2. Подключение Git-репозитория

Harness работает с репозиторием (GitHub/GitLab/Bitbucket). Рекомендуем GitHub.

1. Инициализируйте репозиторий и запушьте проект:

   ```bash
   cd arbitr-ai
   git init
   git add .
   git commit -m "Arbitr AI: MVP платформа + Harness CI/CD"
   git branch -M main
   git remote add origin https://github.com/<ВАШ_ЛОГИН>/arbitr-ai.git
   git push -u origin main
   ```

2. В Harness: **Project → Default → Code Repositories → Connect Repo**:
   - Выберите провайдера (GitHub) и авторизуйте Harness App.
   - Укажите репозиторий `arbitr-ai`.

3. Проверьте, что файлы из `.harness/` видны в репозитории
   (Harness CI может подхватывать их напрямую из Git).

---

## 3. Секреты (НИКОГДА в код!)

Все секреты создаются **только в Harness Secrets Management**.
Реальные значения не хранятся в Git — в YAML-файлах только ссылки.

Создайте секреты (Project → Secrets → New Secret → Text):

| Секрет | Назначение |
|---|---|
| `arbitr_ai_fns_key_dev` / `_stage` / `_prod` | API-ключ ФНС |
| `arbitr_ai_rosreestr_key_prod` | API-ключ Росреестра |
| `arbitr_ai_fssp_key_prod` | API-ключ ФССП |
| `arbitr_ai_post_token_dev` / `_stage` / `_prod` | Токен Почты России |
| `arbitr_ai_openai_key_dev` / `_stage` / `_prod` | OpenAI API key |
| `arbitr_ai_yandexgpt_key_prod` | YandexGPT API key |
| `arbitr_ai_db_url_dev` / `_stage` / `_prod` | PostgreSQL DSN |
| `arbitr_ai_redis_url_dev` / `_stage` / `_prod` | Redis URL |
| `arbitr_ai_jwt_secret_dev` / `_stage` / `_prod` | JWT secret |
| `arbitr_ai_cryptopro_license` | Лицензия КриптоПро |
| `arbitr_ai_smtp_password_prod` | SMTP-пароль |
| `tf_s3_access_key` | Ключ бакета Terraform state |
| `db_password` | Пароль PostgreSQL |
| `telegram_bot_token` | Токен Telegram-бота уведомлений |
| `telegram_chat_id` | ID чата уведомлений |

В рантайме ссылки инжектятся как:
`<+secrets.getValue("arbitr_ai_fns_key_prod")>` — это уже прописано в окружениях.

---

## 4. Kubernetes-кластер для деплоя

Деплой выполняется в K8s через Harness CD. Кластер можно поднять на Yandex Cloud,
или использовать свой (k3s/minikube).

### Вариант A — Yandex Managed Kubernetes (как в Terraform)

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply   # создаст VPC, PostgreSQL, Redis, MinIO, кластер k8s
```

### Вариант B — уже существующий кластер

1. Получите `kubeconfig`:
   ```bash
   kubectl config view --raw > ~/arbitr-ai-kubeconfig.yaml
   ```
2. В Harness: **Project → Environments → New Infrastructure → Kubernetes**:
   - **Name:** `arbitr-ai-k8s`
   - **Connector:** создайте K8s-коннектор с типом **Kubernetes Cluster**
     (вставьте содержимое kubeconfig или используйте service account из
     [`infra/k8s/rbac.yaml`](infra/k8s/rbac.yaml)).
3. Укажите **namespace**: `arbitr-ai` (создаётся из
   [`infra/k8s/namespace.yaml`](infra/k8s/namespace.yaml)):
   ```bash
   kubectl create -f infra/k8s/namespace.yaml
   ```

---

## 5. Импорт пайплайнов и окружений

Конфиги в `.harness/` готовы. В Harness UI импортируйте их (или используйте
Harness Git Experience / Pipeline Studio):

| Файл | Пайплайн |
|---|---|
| `.harness/pipelines/build-and-test-backend.yaml` | CI: backend (ruff, mypy, pytest, Docker, Trivy) |
| `.harness/pipelines/build-and-test-frontend.yaml` | CI: frontend (npm, build, Docker) |
| `.harness/pipelines/deploy-stage.yaml` | CD: deploy в stage (rolling + smoke + telegram) |
| `.harness/pipelines/deploy-prod.yaml` | CD: deploy в prod (approval + blue/green + canary) |
| `.harness/pipelines/infra-provision.yaml` | Terraform: provision инфраструктуры |
| `.harness/environments/dev.yaml` / `stage.yaml` / `prod.yaml` | Окружения с секретами |

Порядок запуска:
1. `infra-provision` — создать инфраструктуру (1 раз).
2. `build-and-test-backend` + `build-and-test-frontend` — на каждый push.
3. `deploy-stage` — выкат на stage.
4. `deploy-prod` — выкат на prod (с ручным approval).

---

## 6. Feature Flags

Флаги уже описаны в [`.harness/feature-flags.yaml`](.harness/feature-flags.yaml):

- `enable_rosreestr_api` — API Росреестра (dev=OFF, stage=ON, prod=ON после пилота)
- `enable_ai_analysis` — генерация документов AI
- `enable_email_delivery` — отправка писем кредиторам
- `enable_notary_integration` — нотариат (смерть должника)
- `enable_rpa_gibdd` — RPA ГИБДД/ГИМС/Гостехнадзор

Импортируйте их в **Project → Feature Flags**, ключ SDK — через секрет
`harness_ff_key`.

---

## 7. Первый деплой

1. Убедитесь, что секреты созданы (шаг 3).
2. Запустите `build-and-test-backend` — артефакт уйдёт в CR (container registry).
3. Запустите `deploy-stage` — сервисы поднимутся в `arbitr-ai` namespace.
4. Проверьте: `curl https://stage.arbitr.ai/health` → `{"status":"ok"}`.
5. После ручного approval — `deploy-prod` (blue/green, canary 5%, rollback).

---

## Диагностика

| Проблема | Решение |
|---|---|
| `Access to the path ... denied` при запуске пайплайна | Проверьте права K8s service account (rbac.yaml) |
| Секрет не подставляется | Проверьте имя/географию секрета, `<+secrets.getValue(...)>` |
| Не найден орг-идентификатор | Убедитесь, что `orgIdentifier: arbitr-ai` совпадает с созданным |
| Кластер не подключается | Проверьте kubeconfig и namespace `arbitr-ai` |