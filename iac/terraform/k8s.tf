# iac/terraform/k8s.tf

# ── 1) Используем всегда актуальный Ubuntu 22.04 LTS ──────
data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

# ── 2) Managed Kubernetes Cluster ─────────────────────────
resource "yandex_kubernetes_cluster" "cluster" {
  name            = "style-cluster"
  folder_id       = var.folder_id
  network_id      = yandex_vpc_network.net.id
  release_channel = "rapid"

  master {
    zonal {
      zone      = var.zone
      subnet_id = yandex_vpc_subnet.subnet.id
    }
    version = "1.27"
  }

  # SA для control-plane и для воркеров
  service_account_id      = var.iam_sa_id
  node_service_account_id = var.node_sa_id
}
# :contentReference[oaicite:0]{index=0}

# ── 3) Node Group (воркеры) ───────────────────────────────
resource "yandex_kubernetes_node_group" "nodes" {
  cluster_id = yandex_kubernetes_cluster.cluster.id
  version    = yandex_kubernetes_cluster.cluster.master[0].version

  instance_template {
    platform_id = "standard-v1"
    nat         = true
    resources {
      cores  = 2
      memory = 4
    }
    boot_disk {
      size = 20
      type = "network-hdd"
    }
    scheduling_policy {
      preemptible = false
    }
  }

  # при старте всегда 2 ноды; автоскейл будет через HPA
  scale_policy {
    fixed_scale {
      size = 2
    }
  }

  allocation_policy {
    location {
      zone      = var.zone
      subnet_id = yandex_vpc_subnet.subnet.id
    }
  }
}
# :contentReference[oaicite:1]{index=1}
