# arbitr-ai — Terraform state & переменные

# Состояние хранится в Yandex Object Storage (бакет) или локально dev
# Для prod обязательно удалённое состояние с блокировками.

# Пример бэкенда:
# terraform {
#   backend "s3" {
#     bucket                      = "arbitr-ai-tfstate"
#     key                         = "prod/terraform.tfstate"
#     region                      = "us-east-1"  # стандартный для Yandex S3
#     endpoint                    = "https://storage.yandexcloud.net"
#     skip_region_validation      = true
#     skip_credentials_validation = true
#     skip_requesting_account_id  = true
#     skip_s3_checksum            = true
#   }
# }

# Секреты НЕ хранить в репозитории! Пароли — через Harness Secrets Management.
# Пример: export TF_VAR_db_password="$(harness secret)"