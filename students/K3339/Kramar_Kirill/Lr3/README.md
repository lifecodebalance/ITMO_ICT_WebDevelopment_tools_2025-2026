# Лабораторная работа 3

Docker, HTTP-прокси для парсера, Celery + Redis.

## Быстрый старт

```bash
cd students/K3339/Kramar_Kirill/Lr3
docker compose up --build
```

Swagger UI: `http://localhost:8000/docs`

## Тест подзадачи 2 (синхронный парсинг)

```bash
curl -X POST "http://localhost:8000/parse?url=https://example.com"
```

## Тест подзадачи 3 (Celery)

```bash
curl -X POST "http://localhost:8000/parse/async?url=https://python.org"
# скопируйте task_id из ответа
curl "http://localhost:8000/parse/async/<task_id>"
```

## Остановка

```bash
docker compose down
```

Подробности — в `docs/`.
