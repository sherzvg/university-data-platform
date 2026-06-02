# Data Product: academic_performance.gold.student_features

## Владелец
Команда «Учебный офис», ответственный: @ivan.ivanov

## Назначение
Витрина признаков студента для прогноза успеваемости и отчисления.

## Интерфейс
- **Формат:** Delta Lake таблица в S3 (s3://unidata-gold/academic_performance/student_features/)
- **Доступ для аналитиков:** через Cube.js / Trino
- **Доступ для ML:** через Feast (offline и online store)
- **Схема:** см. ниже

## Схема таблицы
| Поле | Тип | Описание |
|---|---|---|
| student_id | STRING | PK |
| avg_grade_last_semester | DOUBLE | Средний балл за последний семестр |
| attendance_rate_30d | DOUBLE | Посещаемость за 30 дней (0..1) |
| assignments_submitted_rate | DOUBLE | Доля сданных работ |
| late_submissions_count_30d | INT | Кол-во просрочек |
| risk_score | DOUBLE | Производный признак |
| event_ts | TIMESTAMP | Время расчёта |

## SLA
- **Свежесть:** обновление ежесуточно к 06:00 MSK
- **Полнота:** ≥ 99% студентов активного контингента
- **Доступность:** 99.5% (исключая запланированные окна)

## Метрики качества (Great Expectations)
- `student_id` уникален и непуст
- `avg_grade_last_semester` ∈ [0, 5]
- `attendance_rate_30d` ∈ [0, 1]
- Нет дубликатов по (student_id, event_ts)
- Свежесть: max(event_ts) ≥ now() - 28h

## Версионирование
- Контракт схемы: `contracts/academic_performance/student_features.v1.json`
- Изменения схемы — через PR + ADR