############################################
# 0.  Service Account + роли
############################################
resource "yandex_iam_service_account" "k8s_sa" {
  name      = "hair-k8s-sa"
  folder_id = var.folder_id
}

# Роль «editor» для управления ресурсами каталога
resource "yandex_resourcemanager_folder_iam_member" "k8s_sa_editor" {
  folder_id = var.folder_id
  role      = "editor"
  member    = "serviceAccount:${yandex_iam_service_account.k8s_sa.id}"
}

# Роль на чтение образов из Container Registry
resource "yandex_resourcemanager_folder_iam_member" "k8s_sa_pull" {
  folder_id = var.folder_id
  role      = "container-registry.images.puller"
  member    = "serviceAccount:${yandex_iam_service_account.k8s_sa.id}"
}

############################################
# 1.  VPC и подсеть
############################################
resource "yandex_vpc_network" "net" {
  name = "hair-net"
}

resource "yandex_vpc_subnet" "subnet" {
  name           = "hair-subnet"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.net.id
  v4_cidr_blocks = ["10.10.0.0/24"]
}

############################################
# 2.  PostgreSQL
############################################
resource "yandex_mdb_postgresql_cluster" "db" {
  name        = "hair-postgres"
  environment = "PRESTABLE"
  network_id  = yandex_vpc_network.net.id

  config {
    version = 15
    resources {
      resource_preset_id = "s2.micro"   # 1 vCPU, 1 GB
      disk_size          = 10           # GB
      disk_type_id       = "network-ssd"
    }
  }

  host {
    zone      = "ru-central1-a"
    subnet_id = yandex_vpc_subnet.subnet.id
  }
}

############################################
# 3.  Object Storage
############################################
resource "yandex_storage_bucket" "images" {
  bucket        = "hair-images-${var.folder_id}"
  acl           = "public-read"
  force_destroy = true
}

############################################
# 4.  Kubernetes‑кластер + одна нода
############################################
resource "yandex_kubernetes_cluster" "k8s" {
  name       = "hair-k8s"
  network_id = yandex_vpc_network.net.id

  master {
    version   = "1.29"
    public_ip = true
  }

  service_account_id      = yandex_iam_service_account.k8s_sa.id
  node_service_account_id = yandex_iam_service_account.k8s_sa.id
}

resource "yandex_kubernetes_node_group" "default" {
  name       = "hair-ng"
  cluster_id = yandex_kubernetes_cluster.k8s.id
  version    = "1.29"

  scale_policy {
    fixed_scale {
      size = 1
    }
  }

  # ── шаблон виртуальной машины ──
  instance_template {
    platform_id = "standard-v1"

    resources {
      cores  = 1
      memory = 2
    }

    boot_disk {
      type = "network-hdd"
      size = 30
    }

    network_interface {
      nat        = true
      subnet_ids = [yandex_vpc_subnet.subnet.id]
    }

  }

  allocation_policy {
    location {
      zone = "ru-central1-a"
    }
  }
}


