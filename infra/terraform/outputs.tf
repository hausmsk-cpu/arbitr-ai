# Выходные данные инфраструктуры arbitr-ai

output "postgres_host" {
  value = yandex_mdb_postgresql_cluster.arbitr-ai.host[0].fqdn
}

output "postgres_port" {
  value = 6432  # стандартный порт Yandex Managed PostgreSQL
}

output "redis_host" {
  value = yandex_mdb_redis_cluster.arbitr-ai.host[0].fqdn
}

output "redis_port" {
  value = 6379
}

output "minio_endpoint" {
  value = var.environment == "prod" ? "" : yandex_compute_instance.minio[0].network_interface[0].nat_ip_address
}