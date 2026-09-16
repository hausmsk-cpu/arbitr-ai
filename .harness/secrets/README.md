# ─────────────────────────────────────────────────────────────
# arbitr-ai — Harness Secrets Management
# Секреты создаются в Harness UI, здесь — справочник.
# НИКОГДА не хранить реальные значения в Git!
# ─────────────────────────────────────────────────────────────

# ── API-ключи госорганов ──
# arbitr_ai_fns_key_dev / arbitr_ai_fns_key_stage / arbitr_ai_fns_key_prod
# arbitr_ai_rosreestr_key_prod
# arbitr_ai_fssp_key_prod
# arbitr_ai_post_token_dev / arbitr_ai_post_token_stage / arbitr_ai_post_token_prod

# ── LLM ──
# arbitr_ai_openai_key_dev / arbitr_ai_openai_key_stage / arbitr_ai_openai_key_prod
# arbitr_ai_yandexgpt_key_prod

# ── БД и кэш ──
# arbitr_ai_db_url_dev / arbitr_ai_db_url_stage / arbitr_ai_db_url_prod
# arbitr_ai_redis_url_dev / arbitr_ai_redis_url_stage / arbitr_ai_redis_url_prod

# ── Безопасность ──
# arbitr_ai_jwt_secret_dev / arbitr_ai_jwt_secret_stage / arbitr_ai_jwt_secret_prod
# arbitr_ai_cryptopro_license

# ── Почта / SMTP ──
# arbitr_ai_smtp_password_prod

# ── Инфраструктура ──
# tf_s3_access_key — ключ доступа к бакету Terraform state
# db_password — пароль PostgreSQL

# ── CI/CD ──
# telegram_bot_token — токен Telegram-бота уведомлений
# telegram_chat_id — ID чата для уведомлений

# ─────────────────────────────────────────────────────────────
# Инъекция в runtime через Harness: <+secrets.getValue("имя_секрета")>
# ─────────────────────────────────────────────────────────────