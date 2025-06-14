# 4.2 Развёртывание VM и Docker через Terraform (Stage 4.2)

## Цели этапа
1. Изучить Infrastructure as Code (Terraform) в Yandex Cloud.
2. Через Terraform создать виртуальную машину (VM), сеть и статический IP.
3. Автоматически установить Docker на VM (cloud-init).
4. Запустить контейнеры нашего приложения из Container Registry.

---

## 1. Структура репозитория
```

iac/
├─ stage2/                # старый эксперимент
└─ terraform/             # новый код для этапа 4.2
├─ main.tf            # ресурсы сети, IP, VM + cloud-init
├─ variables.tf       # входные переменные (yc\_token, cloud\_id, ...)
└─ outputs.tf         # вывод public\_ip

````

## 2. Файлы Terraform

### 2.1 `iac/terraform/main.tf`
```hcl
terraform { required_providers { yandex = { source = "yandex-cloud/yandex" version = ">= 0.142.0" } } }
provider "yandex" {
  token     = var.yc_token
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
  zone      = var.zone
}

# VPC network + subnet
resource "yandex_vpc_network" "net" { name = "style-net" }
resource "yandex_vpc_subnet" "subnet" {
  name           = "style-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.net.id
  v4_cidr_blocks = ["192.168.10.0/24"]
}

# Static IP
resource "yandex_vpc_address" "ext_ip" {
  name = "style-ip-stage42"
  external_ipv4_address { zone_id = var.zone }
}

# VM with cloud-init for Docker
resource "yandex_compute_instance" "vm" {
  name        = "style-api-vm"
  platform_id = "standard-v1"
  zone        = var.zone

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

  network_interface {
    subnet_id      = yandex_vpc_subnet.subnet.id
    nat            = true
    nat_ip_address = yandex_vpc_address.ext_ip.external_ipv4_address[0].address
  }

  metadata = {
    serial-port-enable = 1
    user-data = <<-EOF
      #cloud-config
      package_update: true
      packages: [docker.io]
      runcmd:
        - usermod -aG docker ubuntu
        - docker login cr.yandex -u iam -p ${YC_IAM_TOKEN}
        - docker pull cr.yandex/${var.registry}/style-api:latest
        - docker run -d --restart unless-stopped -p 80:8000 --name style-api \
            cr.yandex/${var.registry}/style-api:latest
    EOF
  }
}

data "yandex_compute_image" "ubuntu" { family = "ubuntu-2204-lts" }
````

### 2.2 `iac/terraform/variables.tf`

```hcl
variable "yc_token"   { type = string }
variable "cloud_id"   { type = string }
variable "folder_id"  { type = string }
variable "zone"       { type = string default = "ru-central1-a" }
variable "registry"   { type = string }
```

### 2.3 `iac/terraform/outputs.tf`

```hcl
output "public_ip" {
  description = "Публичный IPv4 адрес VM"
  value       = yandex_vpc_address.ext_ip.external_ipv4_address[0].address
}
```

---

## 3. CI/CD интеграция (GitHub Actions)

В `.github/workflows/ci.yml` добавлен шаг:

```yaml
- name: Apply Terraform
  uses: hashicorp/setup-terraform@v3
  with:
    terraform_version: 1.6.x

- run: |
    cd iac/terraform
    terraform init -input=false
    terraform apply -auto-approve \
      -var "yc_token=${{ secrets.YC_IAM_TOKEN }}" \
      -var "cloud_id=${{ secrets.YC_CLOUD_ID }}" \
      -var "folder_id=${{ secrets.YC_FOLDER_ID }}" \
      -var "registry=${{ secrets.YC_CR_REGISTRY }}"
```

* **Secrets**:

  * `YC_IAM_TOKEN` (IAM-токен `t1.…`)
  * `YC_CLOUD_ID`, `YC_FOLDER_ID` (идентификаторы из Yandex Cloud)
  * `YC_CR_REGISTRY` (ID реестра `crp…`)

## 4. Проверка

```bash
terraform output public_ip
# 51.250.xx.yy
curl http://51.250.xx.yy/health  # {"status":"ok"}
```

**Этап 4.2 завершён**: VM в облаке развернута, Docker установлен и контейнер приложения запущен.
`markdown`
