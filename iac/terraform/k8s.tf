module "k8s" {
  source  = "terraform-yacloud-modules/kubernetes/yandex"
  version = "1.1.0"

  # 1. Общие параметры
  folder_id  = var.folder_id                     # ID вашего каталога
  network_id = yandex_vpc_network.net.id         # сеть из 4.2
  master_locations = [
    {
      zone      = var.zone                        # ru-central1-a
      subnet_id = yandex_vpc_subnet.subnet.id
    }
  ]

  # 2. Сервис-аккаунты
  service_account_name      = "k8s-master-sa"    # Module создаст SA или можно передать ID
  node_service_account_name = "k8s-node-sa"      # Если пусто — будет использован тот же SA

  # 3. Версия и канал
  master_version  = "1.27"
  release_channel = "rapid"

  # 4. Нод-группы
  node_groups = {
    default = {
      cores       = 2
      memory      = 4
      auto_scale = {
        min     = 2
        max     = 5
        initial = 2
      }
      subnet_id   = yandex_vpc_subnet.subnet.id
    }
  }
}
