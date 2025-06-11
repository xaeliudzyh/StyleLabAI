output "public_ip" {
  description = "Публичный IP развернутой VM"
  value       = yandex_vpc_address.ext_ip.external_ipv4_address.address
}
