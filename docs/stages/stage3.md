**Курс:** «Виртуализация и облачные технологии»

**Студент:** Цаголов Георгий (СП МКН, 3 курс)

**Дата:** 23 мая 2025 г.

---

## 1. Сценарии использования (User Stories)

| № | Пользователь    | Цель                                                     | Краткий поток                                                              |
| - | --------------- | -------------------------------------------------------- | -------------------------------------------------------------------------- |
| 1 | Гость           | Просмотреть каталог стрижек                              | `/api/hairstyles` → картинки из S3                                         |
| 2 | Клиент          | Зарегистрироваться, пройти анкету, получить рекомендации | `/api/auth`, `/api/user`, `/api/metrics` (POST answers) → `/api/recommend` |
| 3 | Клиент          | Оценить стрижку                                          | `POST /api/recommend/{id}/rating`                                          |
| 4 | Барбершоп‑админ | Завести салон, добавить сотрудников                      | `POST /api/barbershop`, `POST /api/user` (role=staff)                      |
| 5 | Админ           | Добавить новый опросник                                  | `POST /api/metrics`                                                        |

---

## 2. Роли и доступная функциональность

| Роль              | Доступ                                                                       | Ограничения                      |
| ----------------- | ---------------------------------------------------------------------------- | -------------------------------- |
| anonymous         | `GET /api/hairstyles`, `POST /api/auth`                                      | картинки только в превью         |
| client            | CRUD собственных данных, ответы на опросник, получение рекомендации, рейтинг | JWT access 15 мин, refresh 1 год |
| barbershop\_admin | CRUD своего салона и staff                                                   | видит только своих клиентов      |
| admin             | Полный доступ                                                                | операции журналиируются          |

---

## 3. Архитектурный ландшафт (сводная диаграмма)

```plantuml
@startuml
actor User
actor Barber
actor Admin

boundary FE
component APIGW
node K8s {
  component FastAPI
}
node "Serverless" {
  component ML
}
queue "RabbitMQ (later)" as Q
cloud PG
cloud S3

User --> FE --> APIGW --> FastAPI
Barber --> FE
Admin --> FE

FastAPI --> PG : SQL
FastAPI --> S3 : presigned PUT/GET
FastAPI --> ML : HTTP JSON
ML --> S3 : model weights
FastAPI <-down-> Q : (future async)
@enduml
```

---

## 4. Схема базы данных и объектного хранилища

* **Postgres** — ER‑диаграмма (см. раздел 6) хранит структурированные данные.
* **S3 Bucket** — структура каталогов:

  ```text
  hair-images/
    users/<uuid>.jpg
    barbershops/<id>/cover.jpg
    hairstyles/<id>.jpg
  ```

  Доступ: public‑read, загрузка через presigned URL (PUT).

---

## 5. Протоколы и форматы сообщений

| Канал                   | Протокол           | Формат                                     |
| ----------------------- | ------------------ | ------------------------------------------ |
| Client → APIGW          | HTTPS/REST         | JSON UTF‑8                                 |
| APIGW → FastAPI         | HTTP 1.1           | JSON + JWT Bearer                          |
| FastAPI → ML            | HTTP POST `/infer` | `{features: {...}}` → `{style_ids: [int]}` |
| FastAPI → S3            | Presigned URL (v4) | multipart/form‑data                        |
| Internal async (future) | AMQP (RabbitMQ)    | ProtoBuf                                   |

Пример запроса рекомендации:

```http
POST /api/recommend HTTP/1.1
Authorization: Bearer <jwt>
{
  "client_id": 42,
  "top_k": 3
}
```

Ответ:

```json
{
  "styles": [
    {"id":7,"name":"Pompadour","score":0.91},
    {"id":2,"name":"Crew‑cut","score":0.88}
  ]
}
```

---

## 6. ER‑диаграмма (сокращённый вид)

```plantuml
@startuml
entity users { *id PK; login; password_hash; email; role }
entity clients { *id PK; user_id FK }
entity hairstyles { *id PK; name; image_url }
entity recommendations { *id PK; client_id FK; hairstyle_id FK; model_version; rating }
entity metrics { *metric_id PK; name }
entity user_metrics { *id PK; user_id FK; metric_id FK; date; values jsonb }
entity barbershops { *id PK; name; description; photo_url }
users ||--o{ clients
clients ||--o{ recommendations
hairstyles ||--o{ recommendations
users ||--o{ user_metrics
metrics ||--o{ user_metrics
users ||--o{ barbershops : admin
@enduml
```

---

## 7. План целевой нагрузки

| Тип запроса            | Baseline RPS | Peak RPS | Потребление CPU/под |
| ---------------------- | ------------ | -------- | ------------------- |
| `GET /hairstyles`      | 4            | 20       | 5 ms                |
| `POST /metrics`        | 2            | 10       | 12 ms               |
| `POST /recommend` (ML) | 3            | 15       | 60 ms               |
| **Суммарно**           | **10**       | **50**   | ≈ 70 % 1 vCPU       |

*FastAPI pod (1 vCPU) держит 20 RPS с p95=120 ms. При пике 50 RPS требуется 3 pod.*

---

## 8. Масштабирование вверх/вниз

| Компонент        | ↗ Увеличение нагрузки                                | ↘ Снижение нагрузки      |
| ---------------- | ---------------------------------------------------- | ------------------------ |
| **FastAPI pods** | HPA: CPU>15 % → +1 pod (до 5)                        | CPU<5 % → −1 pod (до 1)  |
| **Node group**   | ручное: увеличить cores/memory или добавить 2‑ю ноду | уменьшить до 1 ноды      |
| **Postgres**     | Vertical: `s2.small` → `s2.medium`                   | downgrade в часы простоя |
| **S3**           | Авто, класс Standard                                 | Lifecycle в Cold class   |

---

## 9. Безопасность и резервирование

* **Transport** — HTTPS TLS 1.3, HSTS 6 мес.
* **Auth** — JWT HS256; refresh‑токен хранится http‑only cookie.
* **Secrets** — DSN PG, JWT‑secret в YC Secrets Manager.
* **Backups** — PG PITR 7 дней + weekly full 30 дней; S3 Versioning.
* **Logging** — YC Cloud Logging; доступ только admin‑role.
* **Monitoring** — Prometheus + Grafana, alert CPU>80 % 5 мин.

---

## 10. Заключение

Документация охватывает все пункты задания: сценарии, роли, архитектурные и физические схемы, БД + S3‑структура, протоколы, расчёт нагрузки и планы масштабирования. Решение укладывается в грант YC, легко масштабируется как вверх, так и вниз.
