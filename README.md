# Университетская платформа данных

Проект по дисциплине «Разработка информационно-аналитических систем»

Платформа реализует концепцию **Data Mesh** для университетской среды: сбор, обработка и анализ данных об успеваемости студентов, загруженности аудиторий и вовлечённости в учебный процесс.

---

## Архитектура

```
LMS API (симулятор)          Kafka Events (СКУД)
        │                           │
        ▼                           ▼
   Airflow DAG              ksqlDB (агрегация)
        │                           │
        ▼                           ▼
  MinIO / S3 (Raw)          ClickHouse (OLAP)
        │                           │
        ▼                           ▼
  Delta Lake (Bronze)         Grafana (Real-time)
        │
        ▼
  Delta Lake (Silver)
        │
        ▼
  Delta Lake (Gold) ──► Feast (Feature Store)
        │
        ▼
  Streamlit (Frontend)
```

### Домены данных (Data Mesh)

| Домен | Назначение |
|---|---|
| `academic_performance` | Оценки, посещаемость, признаки для ML |
| `campus_infrastructure` | Загруженность аудиторий, RFID-проходы |
| `student_engagement` | Активность в LMS, сдача заданий |

---

## Стек технологий

| Слой | Технология |
|---|---|
| Оркестрация | Apache Airflow 2.9 |
| Object Storage | MinIO (S3-совместимый) |
| Потоки | Apache Kafka + ksqlDB |
| Lakehouse | Delta Lake + Apache Spark 3.5 |
| Feature Store | Feast |
| OLAP | ClickHouse 24.3 |
| Мониторинг | Grafana |
| Frontend | Streamlit |
| IaC | Terraform (Yandex.Cloud) |
| CI/CD | GitHub Actions |
| Качество данных | Great Expectations |

---

## Быстрый старт

### Требования
- Windows 10 + WSL2 (Ubuntu 22.04)
- Docker Desktop 4.x с WSL2 интеграцией
- Python 3.10+
- 8 GB RAM минимум

### Запуск стека

```bash
# Клонировать репозиторий
git clone https://github.com/sherzvg/university-data-platform.git
cd university-data-platform

# Запустить все сервисы
cd infra/docker/platform
docker compose up -d

# Проверить статус
docker compose ps
```

### Запуск генератора событий

```bash
cd ~/university-data-platform
python3 -m venv .venv
source .venv/bin/activate
pip install kafka-python==2.0.2
python3 platform/streaming/event_producer.py
```

### Запуск Streamlit фронта

```bash
source .venv/bin/activate
pip install streamlit altair requests
streamlit run platform/frontend/app.py
```

---

## Доступные сервисы после запуска

| Сервис | URL | Логин | Пароль |
|---|---|---|---|
| Airflow UI | http://localhost:8080 | admin | admin |
| MinIO Console | http://localhost:9001 | minioadmin | minioadmin |
| Kafka UI | http://localhost:8082 | — | — |
| Grafana | http://localhost:3000 | admin | admin |
| Streamlit | http://localhost:8501 | — | — |
| LMS API | http://localhost:5001/health | — | — |

---

## Структура проекта

```
university-data-platform/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI/CD
├── docs/
│   ├── adr/                          # Architecture Decision Records
│   │   ├── 0001-local-docker-instead-of-yc.md
│   │   ├── 0002-delta-lake-over-iceberg.md
│   │   ├── 0003-airflow-over-prefect.md
│   │   ├── 0004-ksqldb-over-flink.md
│   │   └── 0005-clickhouse-for-analytics.md
│   ├── data-products/
│   │   ├── domains.md                # Описание доменов Data Mesh
│   │   └── academic-performance.md  # Data Product спецификация
│   └── runbook.md                    # Инструкции по эксплуатации
├── infra/
│   ├── terraform-yc/                 # Terraform конфиги для Yandex.Cloud
│   │   ├── versions.tf
│   │   ├── variables.tf
│   │   ├── storage.tf                # Object Storage + бакеты
│   │   ├── kafka.tf                  # Managed Kafka кластер
│   │   ├── vm.tf                     # Compute VM под Airflow
│   │   └── cloud-init.yaml
│   └── docker/platform/
│       ├── docker-compose.yml        # Локальный стек (9 сервисов)
│       └── airflow/
│           └── dags/
│               └── raw_academic_performance.py
├── platform/
│   ├── lms_simulator/
│   │   └── lms_api.py                # Flask симулятор LMS API
│   ├── spark_jobs/
│   │   ├── bronze_to_silver_grades.py
│   │   └── silver_to_gold_student_features.py
│   ├── streaming/
│   │   └── event_producer.py         # Kafka event generator
│   ├── great_expectations/
│   │   └── setup_ge.py               # GE валидация данных
│   ├── feature_store/
│   │   └── unidata_feast/            # Feast Feature Store
│   └── frontend/
│       └── app.py                    # Streamlit UI
└── tests/
    └── unit/
        └── test_transformations.py   # Unit тесты трансформаций
```

---

## Data Product: academic_performance

Главный Data Product платформы — витрина признаков студента.

**Интерфейс:** Delta Lake таблица в `s3://unidata-gold/academic_performance/student_features/`

| Поле | Тип | Описание |
|---|---|---|
| student_id | STRING | Идентификатор студента |
| avg_grade_last_30d | DOUBLE | Средний балл за 30 дней |
| attendance_rate_30d | DOUBLE | Посещаемость (0..1) |
| grades_count_30d | INT | Количество оценок за 30 дней |
| risk_score | DOUBLE | Риск отчисления (0..1) |
| event_ts | TIMESTAMP | Время расчёта |

**SLA:** обновление ежесуточно, свежесть ≤28 часов, полнота ≥99%

---

## CI/CD Pipeline

GitHub Actions запускается на каждый push в `main`:

1. **lint** — проверка кода (ruff + black)
2. **unit-tests** — pytest тесты трансформаций
3. **validate-dag** — синтаксическая проверка Airflow DAG

---

## Облачная инфраструктура (Terraform)

Terraform-конфигурации описывают инфраструктуру Yandex.Cloud:

```bash
cd infra/terraform-yc
terraform init
terraform plan
```

Создаются ресурсы:
- 5 бакетов Object Storage (raw, bronze, silver, gold, artifacts)
- Managed Kafka кластер (1 брокер, 2 топика)
- Compute VM 4 vCPU / 8 GB под Airflow
- VPC сеть и подсеть

> **Примечание:** для университетского аккаунта YC платные сервисы могут быть ограничены на уровне организации. Локальный Docker Compose стек является полнофункциональной заменой с совместимыми API.

---

## Архитектурные решения (ADR)

| ADR | Решение | Обоснование |
|---|---|---|
| [0001](docs/adr/0001-local-docker-instead-of-yc.md) | Docker вместо YC | Ограничения квот университетского облака |
| [0002](docs/adr/0002-delta-lake-over-iceberg.md) | Delta Lake | Зрелость, интеграция со Spark |
| [0003](docs/adr/0003-airflow-over-prefect.md) | Airflow | Широкое сообщество, TaskFlow API |
| [0004](docs/adr/0004-ksqldb-over-flink.md) | ksqlDB | SQL-интерфейс, меньше boilerplate |
| [0005](docs/adr/0005-clickhouse-for-analytics.md) | ClickHouse | Kafka Engine, быстрые аналитические запросы |

---

## Автор

**Sherzotbek Yuldashev**
Курс: Разработка информационно-аналитических систем