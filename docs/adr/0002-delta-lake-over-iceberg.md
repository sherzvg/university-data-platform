# ADR 0002: Delta Lake вместо Apache Iceberg

## Статус
Принято.

## Контекст
Нужен open table format для Lakehouse с ACID-транзакциями.

## Решение
Выбран Delta Lake 3.x.

## Обоснование
- Зрелая экосистема, больше туториалов
- Тесная интеграция со Spark из коробки
- Совместимость с Pandas через delta-rs
- Достаточно для академического кейса (single writer)

## Альтернативы
- Iceberg: лучше для multi-engine, но больше boilerplate
- Hudi: меньше сообщества
