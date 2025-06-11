# Отчет по этапу 4.3: Оркестрация в Kubernetes

**Цели этапа 4.3:**

1. Изучить основы Kubernetes.
2. Развернуть кластер и запустить приложение из Docker-образа.
3. Настроить горизонтальное масштабирование (HPA) при нагрузке ≥15% CPU.
4. Внедрить мониторинг (Prometheus + Grafana).

---

## Что уже реализовано

1. **Kubernetes-кластер**

   * Описан в Terraform (`iac/terraform/k8s.tf`):

     * Ресурс `yandex_kubernetes_cluster.cluster` с зональным мастер-подразделением.
     * Ресурс `yandex_kubernetes_node_group.nodes` для worker-нод (2 узла, 2 CPU/4GiB).
   * Входные переменные `iam_sa_id` и `node_sa_id` заданы и прокинуты из GitHub Secrets.
   * Outputs `cluster_id` и `node_group_id` добавлены в `outputs.tf`.

2. **Деплой приложения**

   * Создан каталог `k8s/` с манифестами:

     * `namespace.yaml` — пространство `style`.
     * `deployment.yaml` — Deployment style-api (2 реплики, readinessProbe).
     * `service.yaml` — Service Type=LoadBalancer (порт 80→8000).
     * `hpa.yaml` — HPA (min=2, max=5, Target CPU=15%).
   * CI-шаг в `.github/workflows/ci.yml` применяет эти файлы через `kubectl apply`.

3. **Мониторинг**

   * Добавлен шаг `helm install monitoring prometheus-community/kube-prometheus-stack`.
   * В пространстве `monitoring` установлен Prometheus Operator + Grafana.
   * Дашборды CPU, Memory и latency автоматически собирают метрики подов.

4. **CI/CD**

   * Workflow разбит на два job’а:

     1. `test-build` — тесты + сборка Docker-образа `style-api`.
     2. `deploy-infra` — `terraform apply` для поднятия кластера + `kubectl apply` + Helm.
   * Пайплайн полностью автоматизирован: от коммита в main до запуска приложения.

---

## Результаты проверки

* **Terraform** успешно создаёт кластер и пул нод.
* **kubectl get nodes** показывает 2 READY узла.
* **kubectl get pods,svc,hpa -n style**:

  * 2 Pod’а `style-api`, Service с External IP, HPA в статусе Active.
* **Grafana** доступна портом (port-forward) и показывает метрики по подам.
* **CI/CD** не проходят. Весь вечер копался - не смог, но для частичного решения думаю более чем хватает

