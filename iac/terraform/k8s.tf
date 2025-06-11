# iac/terraform/k8s.tf

###############################################################################
# 1) Актуальный Ubuntu 22.04 LTS для нод
###############################################################################
data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

###############################################################################
# 2) Managed Kubernetes Cluster (control plane)
###############################################################################
resource "yandex_kubernetes_cluster" "cluster" {
  name            = "style-cluster"
  folder_id       = var.folder_id
  network_id      = yandex_vpc_network.net.id         # ресурс из main.tf
  release_channel = "rapid"

  master {
    # блок zonal указывает зону и существующую подсеть
    zonal {
      zone      = var.zone
      subnet_id = yandex_vpc_subnet.subnet.id         # ресурс из main.tf
    }
    version = "1.27"
  }

  service_account_id      = var.iam_sa_id            # SA для control plane
  node_service_account_id = var.node_sa_id           # SA для worker nodes
}

###############################################################################
# 3) Node Group (worker nodes)
###############################################################################
resource "yandex_kubernetes_node_group" "nodes" {
  name       = "style-node-group"
  cluster_id = yandex_kubernetes_cluster.cluster.id
  version    = yandex_kubernetes_cluster.cluster.master[0].version

  # куда вбросить ноды: та же подсеть
  allocation_policy {
    location {
      zone      = var.zone
      subnet_id = yandex_vpc_subnet.subnet.id
    }
  }

  # всегда два нода, автоскейл (HPA) будет на уровне Deployment
  scale_policy {
    fixed_scale {
      size = 2
    }
  }

  instance_template {
    platform_id = "standard-v1"
    resources {
      cores  = 2
      memory = 4
    }
    boot_disk {
      initialize_params {
        image_id = data.yandex_compute_image.ubuntu.id
        size     = 20
      }
    }
    scheduling_policy {
      preemptible = false
    }
  }
}
