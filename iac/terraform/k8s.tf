data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

resource "yandex_kubernetes_cluster" "cluster" {
  name            = "style-cluster"
  folder_id       = var.folder_id
  network_id      = yandex_vpc_network.net.id
  release_channel = "RAPID"

  master {
    zonal {
      zone      = var.zone
      subnet_id = yandex_vpc_subnet.subnet.id
    }
    public_ip = true
  }
  service_account_id      = var.iam_sa_id
  node_service_account_id = var.node_sa_id
}

resource "yandex_kubernetes_node_group" "nodes" {
  name       = "style-node-group"
  cluster_id = yandex_kubernetes_cluster.cluster.id
  version    = yandex_kubernetes_cluster.cluster.master[0].version

  allocation_policy {
    location {
      zone      = var.zone
      subnet_id = yandex_vpc_subnet.subnet.id
    }
  }

  scale_policy {
    fixed_scale {
      size = 2
    }
  }

  instance_template {
    platform_id = "standard-v1"

    network_interface {
      subnet_ids = [ yandex_vpc_subnet.subnet.id ]
      nat        = true
    }

    resources {
      cores  = 2
      memory = 4
    }

    boot_disk {
      size = 64
      type = "network-hdd"
    }

    scheduling_policy {
      preemptible = false
    }
  }
}


