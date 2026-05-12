# Подготовка и запуск

## 1. Установка зависимостей

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Настройка `.env`

Создайте файл `.env` в корне ЛР2 (можно скопировать из примера):

```bash
cp .env.example .env
```

Главная переменная:

```env
DB_TIME=...
```

Должна указывать на **ту же БД, что и в ЛР1**.

## 3. Подготовка схемы БД

Так как ЛР2 пишет в таблицы ЛР1 (`user`, `taskcategory`, `task`), они должны уже существовать.

Если используете PostgreSQL и миграции ЛР1, сначала выполните в проекте ЛР1:

```bash
alembic upgrade head
```

## 4. Запуск задачи 1 (сумма)

```bash
PYTHONPATH=src python -m lr2.task1.run_benchmark --workers 4
```

Можно запускать и отдельные варианты:

```bash
PYTHONPATH=src python -m lr2.task1.threading_sum
PYTHONPATH=src python -m lr2.task1.multiprocessing_sum
PYTHONPATH=src python -m lr2.task1.async_sum
```

## 5. Запуск задачи 2 (парсинг + БД)

```bash
PYTHONPATH=src python -m lr2.task2.run_benchmark --workers 3
```

Или по отдельности:

```bash
PYTHONPATH=src python -m lr2.task2.threading_parser
PYTHONPATH=src python -m lr2.task2.multiprocessing_parser
PYTHONPATH=src python -m lr2.task2.async_parser
```

## 6. Запуск документации

```bash
mkdocs serve
```

Откройте локальный адрес, который покажет консоль (обычно `http://127.0.0.1:8000`).

## Технические нюансы

- Для `multiprocessing` используется `if __name__ == "__main__"` и `freeze_support()` — это важно для Windows-режима `spawn`.
- Для `aiohttp` добавлен явный SSL-контекст через `certifi`, чтобы избежать проблем с сертификатами.
- Для async SQLAlchemy нужен `greenlet` — он добавлен в `requirements.txt`.
