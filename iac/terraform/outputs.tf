output "cluster_id" {
  value = yandex_kubernetes_cluster.cluster.id
}

output "node_group_id" {
  value = yandex_kubernetes_node_group.nodes.id
}