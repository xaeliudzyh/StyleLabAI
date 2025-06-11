output "public_ip" {
  description = "Public IP of the VM"
  value       = yandex_vpc_address.ext_ip.external_ipv4_address[0].address
}

output "cluster_id" {
  value = yandex_kubernetes_cluster.cluster.id
}

output "node_group_id" {
  value = yandex_kubernetes_node_group.nodes.id
}