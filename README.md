# electric-scooter-violation-detection
AI-powered system for detecting violations with electric scooters using computer vision

Дипломный проект: Система мониторинга нарушений с электросамокатами с использованием компьютерного зрения.

## Архитектура

Система состоит из двух основных сервисов:
- **Python-сервис (AI Engine)** - компьютерное зрение и анализ нарушений
- **Java-бэкенд (Spring Boot)** - управление данными, API и бизнес-логика

## Структура проекта
- `traffic-violation-monitoring/` - корневая директория
  - `backend/` - Java Spring Boot бэкенд
  - `ai-engine/` - Python сервис с ML
  - `docs/` - Документация
  - `shared/` - Общие ресурсы
  - `docker-compose.yml` - Запуск всей системы
