variable "yandex_cloud_id" {
  description = "Yandex Cloud ID"
  type        = string
  default     = ""
}

variable "yandex_folder_id" {
  description = "Yandex Cloud Folder ID"
  type        = string
  default     = ""
}

variable "yandex_zone" {
  description = "Yandex Cloud availability zone"
  type        = string
  default     = "ru-central1-a"
}

variable "environment" {
  description = "Environment: dev | stage | prod"
  type        = string
  default     = "dev"
}

variable "db_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}