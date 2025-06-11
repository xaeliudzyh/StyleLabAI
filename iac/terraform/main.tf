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
data "yandex_vpc_network" "net" {
  name = "style-net"
}
data "yandex_vpc_subnet" "subnet" {
  network_id = data.yandex_vpc_network.net.id
  zone       = var.zone
  name       = "style-subnet"
}
data "yandex_vpc_address" "ext_ip" {
  name = "style-ip-stage42"  # или как вы его назвали
}

