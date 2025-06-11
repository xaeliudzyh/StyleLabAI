output "public_ip" {
  description = "Public IP of the VM"
  value       = yandex_vpc_address.ext_ip.external_ipv4_address[0].address
}