data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

resource "yandex_kubernetes_cluster" "cluster" {
  name       = "style-cluster"
  folder_id  = var.folder_id
  network_id = yandex_vpc_network.net.id
  zone       = var.zone
  release_channel = "rapid"

  master {
    public_ip { subnet_id = yandex_vpc_subnet.subnet.id }
    version   = "1.27"
  }

  service_account_id = var.iam_sa_id
}

resource "yandex_kubernetes_node_group" "nodes" {
  name       = "style-node-group"
  cluster_id = yandex_kubernetes_cluster.cluster.id
  folder_id  = var.folder_id

  node_service_account_id = var.node_sa_id
  subnet_id               = yandex_vpc_subnet.subnet.id
  version                 = yandex_kubernetes_cluster.cluster.master[0].version

  scale_policy {
    auto_scale {
      min_replicas = 2
      max_replicas = 5
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
  }
}
