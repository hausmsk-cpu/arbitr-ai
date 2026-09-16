# arbitr-ai — Infra
# Terraform для развёртывания инфраструктуры: PostgreSQL, Redis, MinIO, Kubernetes.

terraform {
  required_version = ">= 1.5"

  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "~> 0.130"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.15"
    }
  }
}

# ─────────────────────────────────────────────
# Провайдер Yandex Cloud (замените значения)
# ─────────────────────────────────────────────
provider "yandex" {
  cloud_id  = var.yandex_cloud_id
  folder_id = var.yandex_folder_id
  zone      = var.yandex_zone
}

# ─────────────────────────────────────────────
# Managed PostgreSQL
# ─────────────────────────────────────────────
resource "yandex_mdb_postgresql_cluster" "arbitr-ai" {
  name               = "arbitr-ai-db"
  environment        = var.environment
  network_id         = yandex_vpc_network.arbitr-ai.id
  security_group_ids = [yandex_vpc_security_group.db.id]

  config {
    version = "16"
    resources {
      resource_preset_id = "s2.micro"
      disk_type_id       = "network-ssd"
      disk_size          = 20
    }
  }

  host {
    zone             = var.yandex_zone
    subnet_id        = yandex_vpc_subnet.arbitr-ai.id
    assign_public_ip = false
  }
}

resource "yandex_mdb_postgresql_database" "arbitr-ai" {
  cluster_id = yandex_mdb_postgresql_cluster.arbitr-ai.id
  name       = "arbitr-ai"
  owner      = "arbitr-ai"

  depends_on = [yandex_mdb_postgresql_user.arbitr-ai]
}

resource "yandex_mdb_postgresql_user" "arbitr-ai" {
  cluster_id = yandex_mdb_postgresql_cluster.arbitr-ai.id
  name       = "arbitr-ai"
  password   = var.db_password
}

# ─────────────────────────────────────────────
# Managed Redis
# ─────────────────────────────────────────────
resource "yandex_mdb_redis_cluster" "arbitr-ai" {
  name        = "arbitr-ai-redis"
  environment = var.environment
  network_id  = yandex_vpc_network.arbitr-ai.id

  config {
    version  = "7.0"
    password = var.db_password
  }

  resources {
    resource_preset_id = "hm1.nano"
    disk_type_id       = "network-ssd"
    disk_size          = 10
  }

  host {
    zone      = var.yandex_zone
    subnet_id = yandex_vpc_subnet.arbitr-ai.id
  }
}

# ─────────────────────────────────────────────
# MinIO (single-node, dev/stage) — в prod замените на managed S3
# ─────────────────────────────────────────────
resource "yandex_compute_instance" "minio" {
  count = var.environment == "prod" ? 0 : 1

  name        = "arbitr-ai-minio"
  platform_id = "standard-v3"
  zone        = var.yandex_zone

  resources {
    cores  = 2
    memory = 4
  }

  boot_disk {
    initialize_params {
      image_id = "fd8...ubuntu" # замените на актуальный image_id Ubuntu 22.04
      size     = 20
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.arbitr-ai.id
    nat       = true
  }

  metadata = {
    user-data = <<-EOF
      #cloud-config
      runcmd:
        - apt-get update && apt-get install -y docker.io docker-compose
        - docker run -d --name minio -p 9000:9000 minio/minio server /data --console-address ":9001"
    EOF
  }
}

# ─────────────────────────────────────────────
# Сеть и подсеть
# ─────────────────────────────────────────────
resource "yandex_vpc_network" "arbitr-ai" {
  name = "arbitr-ai-net"
}

resource "yandex_vpc_subnet" "arbitr-ai" {
  name           = "arbitr-ai-subnet"
  zone           = var.yandex_zone
  network_id     = yandex_vpc_network.arbitr-ai.id
  v4_cidr_blocks = ["10.1.0.0/24"]
}

resource "yandex_vpc_security_group" "db" {
  name       = "arbitr-ai-db-sg"
  network_id = yandex_vpc_network.arbitr-ai.id

  ingress {
    protocol       = "TCP"
    port           = 5432
    v4_cidr_blocks = ["10.1.0.0/24"]
  }

  ingress {
    protocol       = "TCP"
    port           = 6379
    v4_cidr_blocks = ["10.1.0.0/24"]
  }
}

# ─────────────────────────────────────────────
# Yandex Managed Kubernetes (для деплоя через Harness)
# ─────────────────────────────────────────────
resource "yandex_kubernetes_cluster" "arbitr_ai" {
  name       = "arbitr-ai-k8s"
  network_id = yandex_vpc_network.arbitr-ai.id

  master {
    version   = "1.29"
    public_ip = true

    zonal {
      zone      = var.yandex_zone
      subnet_id = yandex_vpc_subnet.arbitr-ai.id
    }

    security_group_ids = [yandex_vpc_security_group.k8s_master.id]
  }

  service_account_id      = yandex_iam_service_account.arbitr_ai_sa.id
  node_service_account_id = yandex_iam_service_account.arbitr_ai_sa.id

  depends_on = [yandex_vpc_security_group.k8s_master]
}

resource "yandex_kubernetes_node_group" "arbitr_ai_nodes" {
  name       = "arbitr-ai-nodes"
  cluster_id = yandex_kubernetes_cluster.arbitr_ai.id
  version    = "1.29"

  instance_template {
    platform_id = "standard-v3"

    resources {
      memory = 4
      cores  = 2
    }

    boot_disk {
      size = 30
      type = "network-ssd"
    }

    network_interface {
      subnet_ids = [yandex_vpc_subnet.arbitr-ai.id]
      nat        = true
    }

    scheduling_policy {
      preemptible = var.environment != "prod"
    }
  }

  scale_policy {
    fixed_scale {
      size = var.environment == "prod" ? 3 : 1
    }
  }
}

resource "yandex_iam_service_account" "arbitr_ai_sa" {
  name = "arbitr-ai-sa"
}

resource "yandex_resourcemanager_folder_iam_member" "arbitr_ai_sa_editor" {
  folder_id  = var.yandex_folder_id
  role       = "editor"
  member     = "serviceAccount:${yandex_iam_service_account.arbitr_ai_sa.id}"
  depends_on = [yandex_iam_service_account.arbitr_ai_sa]
}

# Security group для master-ноды K8s
resource "yandex_vpc_security_group" "k8s_master" {
  name       = "arbitr-ai-k8s-master-sg"
  network_id = yandex_vpc_network.arbitr-ai.id

  ingress {
    protocol       = "TCP"
    port           = 6443
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol       = "TCP"
    port           = 443
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol       = "ANY"
    from_port      = 0
    to_port        = 65535
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

# ─────────────────────────────────────────────
# Вывод для подключения кластера к Harness
# ─────────────────────────────────────────────
output "k8s_cluster_id" {
  value = yandex_kubernetes_cluster.arbitr_ai.id
}

output "k8s_cluster_endpoint" {
  value = yandex_kubernetes_cluster.arbitr_ai.master[0].external_v4_endpoint
}