# Terraform для Harness — организация Arbitr AI
#
# Применение (после создания API-токена):
#   export HARNESS_PLATFORM_API_KEY="<токен>"
#   cd infra/harness-terraform
#   terraform init
#   terraform plan
#   terraform apply
#
# Провайдер: integrations/harness (terraform-provider-harness)

terraform {
  required_providers {
    harness = {
      source  = "harness/harness"
      version = "~> 0.36"
    }
  }
}

provider "harness" {
  platform_api_key = var.harness_platform_api_key
  endpoint         = "https://app.harness.io/gateway"
}

variable "harness_platform_api_key" {
  type        = string
  description = "API-ключ Harness (Account API Key)"
  sensitive   = true
}

# ── Организация Arbitr Ai ──
resource "harness_platform_organization" "arbitr_ai" {
  identifier = "arbitr-ai"
  name       = "Arbitr AI"
  description = "Организация Arbitr AI — AI-платформа финансового управляющего"
}

# ── Проект Arbitr AI Platform ──
resource "harness_platform_project" "arbitr_ai_platform" {
  identifier = "arbitr-ai-platform"
  name       = "Arbitr AI Platform"
  org_id     = harness_platform_organization.arbitr_ai.id
  description = "Платформа автоматизации финансового управляющего (банкротство ФЛ)"
  color      = "#0063F7"
}

# ── Секреты (placeholder; реальные значения — в Harness UI/CLI) ──
resource "harness_platform_secret_text" "fns_key_dev" {
  identifier = "arbitr_ai_fns_key_dev"
  name       = "arbitr_ai_fns_key_dev"
  org_id     = harness_platform_organization.arbitr_ai.id
  project_id = harness_platform_project.arbitr_ai_platform.id
  secret_manager_identifier = "harnessSecretManager"
  value_type = "Inline"
  value      = "REPLACE_ME_FNS_DEV"
}

resource "harness_platform_secret_text" "fns_key_prod" {
  identifier = "arbitr_ai_fns_key_prod"
  name       = "arbitr_ai_fns_key_prod"
  org_id     = harness_platform_organization.arbitr_ai.id
  project_id = harness_platform_project.arbitr_ai_platform.id
  secret_manager_identifier = "harnessSecretManager"
  value_type = "Inline"
  value      = "REPLACE_ME_FNS_PROD"
}

resource "harness_platform_secret_text" "openai_key_dev" {
  identifier = "arbitr_ai_openai_key_dev"
  name       = "arbitr_ai_openai_key_dev"
  org_id     = harness_platform_organization.arbitr_ai.id
  project_id = harness_platform_project.arbitr_ai_platform.id
  secret_manager_identifier = "harnessSecretManager"
  value_type = "Inline"
  value      = "REPLACE_ME_OPENAI_DEV"
}

resource "harness_platform_secret_text" "db_url_prod" {
  identifier = "arbitr_ai_db_url_prod"
  name       = "arbitr_ai_db_url_prod"
  org_id     = harness_platform_organization.arbitr_ai.id
  project_id = harness_platform_project.arbitr_ai_platform.id
  secret_manager_identifier = "harnessSecretManager"
  value_type = "Inline"
  value      = "REPLACE_ME_DB_URL_PROD"
}

resource "harness_platform_secret_text" "jwt_secret_prod" {
  identifier = "arbitr_ai_jwt_secret_prod"
  name       = "arbitr_ai_jwt_secret_prod"
  org_id     = harness_platform_organization.arbitr_ai.id
  project_id = harness_platform_project.arbitr_ai_platform.id
  secret_manager_identifier = "harnessSecretManager"
  value_type = "Inline"
  value      = "REPLACE_ME_JWT_PROD"
}

# ── Kubernetes-коннектор (подключается к кластеру для CD) ──
resource "harness_platform_connector_kubernetes" "arbitr_ai_k8s" {
  identifier = "arbitr_ai_k8s"
  name       = "Arbitr AI K8s"
  org_id     = harness_platform_organization.arbitr_ai.id
  project_id = harness_platform_project.arbitr_ai_platform.id

  delegate_selectors = ["arbitr-ai-delegate"]

  inherit_from_delegate {
    delegate_name = "harness-delegate"
  }
}

# ── Выходные данные ──
output "organization_id" {
  value = harness_platform_organization.arbitr_ai.id
}

output "project_id" {
  value = harness_platform_project.arbitr_ai_platform.id
}