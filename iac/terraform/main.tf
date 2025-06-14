########################################
# Terraform & provider
########################################
terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = ">= 0.141"
    }
  }
}
provider "yandex" {
  token     = var.yc_token          # приходит из secrets или tfvars
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
  zone      = var.zone
}

resource "yandex_vpc_network" "net" { name = "style-net" }

resource "yandex_vpc_subnet" "subnet" {
  name           = "style-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.net.id
  v4_cidr_blocks = ["192.168.10.0/24"]
}

resource "yandex_vpc_address" "ext_ip" {
  name = "style-ip"
  external_ipv4_address { zone_id = var.zone }
}

resource "yandex_compute_instance" "vm" {
  name        = "style-vm"
  platform_id = "standard-v1"
  zone        = var.zone

  resources {
    cores  = 2
    memory = 4
  }


  boot_disk {
    initialize_params {
      image_id = "fd83m7rp3r4l12c2keph"
      size     = 20
    }
  }

  network_interface {
    subnet_id  = yandex_vpc_subnet.subnet.id
    nat        = true
    nat_ip_address = yandex_vpc_address.ext_ip.external_ipv4_address[0].address
  }


  metadata = {
    serial-port-enable = 1

    user-data = <<-CLOUD
      #cloud-config
      package_update: true
      packages: [docker.io]

      ## добавляем ubuntu в группу docker
      runcmd:
        - usermod -aG docker ubuntu

        # логинимся в Container Registry
        - docker login cr.yandex -u iam -p ${var.yc_token}

        # тянем последний образ
        - docker pull cr.yandex/${var.registry}/style-api:latest

        # запускаем контейнер и пробрасываем порт 80 → 8000
        - docker run -d --restart unless-stopped -p 80:8000 --name style-api \
            cr.yandex/${var.registry}/style-api:latest
    CLOUD
  }
}
