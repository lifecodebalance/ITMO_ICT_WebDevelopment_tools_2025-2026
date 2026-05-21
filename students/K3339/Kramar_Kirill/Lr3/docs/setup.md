# Запуск

## Требования

- Docker Desktop (macOS, Windows) или Docker Engine + Docker Compose Plugin (Linux)
- Порты 5432, 6379, 8000, 8001 должны быть свободны

## Структура файлов

```
students/K3339/Kramar_Kirill/
├── Lr1/          ← FastAPI-приложение + Dockerfile
├── Lr2/          ← Парсер + Dockerfile.parser + parser_api.py
└── Lr3/          ← docker-compose.yml  ← вы здесь
```

## Запуск (все платформы)

```bash
# 1. Перейдите в папку Lr3
cd students/K3339/Kramar_Kirill/Lr3

# 2. (Опционально) скопируйте .env.example и отредактируйте SECRET_KEY
cp .env.example .env

# 3. Соберите образы и запустите все сервисы
docker compose up --build
```

Первый запуск занимает 2–5 минут (скачиваются базовые образы, устанавливаются зависимости).

> На Windows используйте терминал PowerShell или Git Bash. Docker Desktop должен быть запущен.

## Проверка

После успешного старта:

| Адрес | Что открыть |
|---|---|
| `http://localhost:8000/docs` | Swagger UI FastAPI (ЛР1 + новые эндпоинты) |
| `http://localhost:8001/docs` | Swagger UI Parser-сервиса |
| `http://localhost:8000/` | Проверка, что API живой |
| `http://localhost:8001/health` | Проверка, что парсер живой |

## Тестирование эндпоинтов

### Синхронный парсинг (Подзадача 2)

```bash
curl -X POST "http://localhost:8000/parse?url=https://example.com"
```

Ожидаемый ответ:
```json
{"url": "https://example.com", "title": "Example Domain", "saved_to_db": true}
```

### Асинхронный парсинг через Celery (Подзадача 3)

```bash
# Отправить задачу в очередь
curl -X POST "http://localhost:8000/parse/async?url=https://python.org"
# Вернёт {"task_id": "abc-123...", "message": "Task submitted..."}

# Проверить статус (подставьте свой task_id)
curl "http://localhost:8000/parse/async/abc-123..."
# Вернёт {"task_id": "...", "status": "SUCCESS", "result": {"url": "...", "title": "..."}}
```

## Остановка

```bash
docker compose down          # остановить, сохранить БД
docker compose down -v       # остановить и удалить volume с БД
```

## Пересборка после изменения кода

```bash
docker compose up --build
```
