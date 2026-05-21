# Подзадача 1 — Docker

## Зачем Docker

Без Docker каждый разработчик устанавливает зависимости вручную, и версии расходятся.
Docker упаковывает приложение со всеми зависимостями в образ, который одинаково работает на любой машине.

## Dockerfile для API (Lr1)

Файл: `Lr1/Dockerfile`

```dockerfile
FROM python:3.12-slim      # минимальный образ Python

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt   # устанавливаем зависимости

COPY . .                   # копируем весь код

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Ключевые решения:
- `python:3.12-slim` — Debian-slim без лишних системных пакетов, экономит размер образа.
- `psycopg[binary]` в requirements включает скомпилированный libpq, поэтому отдельные системные библиотеки не нужны.
- В docker-compose CMD переопределяется: сначала запускаются миграции Alembic, потом uvicorn.

## Dockerfile для парсера (Lr2)

Файл: `Lr2/Dockerfile.parser`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn requests beautifulsoup4 certifi python-dotenv

COPY src/ src/       # код lr2-пакета
COPY parser_api.py . # точка входа FastAPI

CMD ["uvicorn", "parser_api:app", "--host", "0.0.0.0", "--port", "8001"]
```

Парсер — намеренно лёгкий сервис: не нужна БД, Celery, аутентификация. Только HTTP + HTML-парсинг.

## docker-compose.yml

Файл: `Lr3/docker-compose.yml`

Управляет всеми пятью сервисами как единым стеком.

Важные детали:

### healthcheck для PostgreSQL

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d time_manager_db"]
  interval: 5s
  retries: 10
```

Сервис `api` и `celery_worker` объявлены с `depends_on: postgres: condition: service_healthy`.
Это гарантирует, что Alembic-миграции запустятся только когда БД готова принимать соединения.

### Миграции при старте API

```yaml
command: >
  sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"
```

`alembic upgrade head` — идемпотентная операция: если миграции уже применены, она просто ничего не делает.

### Общая сеть

Docker Compose автоматически создаёт внутреннюю сеть для всех сервисов.
Внутри неё сервисы обращаются друг к другу по имени сервиса:
- `api` → `parser:8001`
- `celery_worker` → `redis:6379` и `parser:8001`
- `api` → `postgres:5432`

### Volumes

```yaml
volumes:
  postgres_data:
```

Данные БД сохраняются в именованном volume — не теряются при перезапуске контейнера.
