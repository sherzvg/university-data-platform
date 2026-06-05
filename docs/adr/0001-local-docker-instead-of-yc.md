# ADR 0001: Локальный Docker Compose вместо Yandex.Cloud

## Статус
Принято.

## Контекст
ТЗ предполагает развёртывание в облаке через Terraform. Использовался университетский YC-аккаунт.

## Проблема
Квоты на платные сервисы (Object Storage, Compute, Managed Kafka) заблокированы на уровне организации. При `terraform apply` — `PermissionDenied` от organization-manager.

## Решение
- Terraform-конфигурации для YC сохранены как артефакт (`infra/terraform-yc/`)
- Рабочий стенд развёрнут через Docker Compose: MinIO (S3 API), Apache Kafka, Airflow

## Последствия
+ Платформа работает сразу, не зависит от облачных квот
+ Полностью воспроизводимо: `docker compose up -d`
- На защите нужно пояснить выбор
