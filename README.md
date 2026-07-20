# electric-scooter-violation-detection
AI-powered system for detecting violations with electric scooters using computer vision

Дипломный проект: Комплексная система мониторинга нарушений правил пользования электросамокатами с использованием технологий компьютерного зрения.

Система автоматизирует выявление таких нарушений, как езда вдвоем на одном самокате, передвижение по запрещенным зонам и оставление элекросамоката в запрещенной зоне.

## Технологический стек

* **AI Engine (Python):** YOLO11m (детекция), YOLO11-pose (оценка поз), PyTorch, Random Forest / Gradient Boosting (scikit-learn), Pandas.
* **Backend (Java):** Java 17, Spring Boot 3.
* **Infrastructure & DB:** PostgreSQL, Redis, MinIO (хранилище медиафайлов нарушений), Docker, Docker Compose, Nginx (reverse proxy).

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
