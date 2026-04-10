# Запуск проекта

## Требования

- Python 3.10+
- PostgreSQL
- установленный `pip`

## Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Для Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка окружения

Создай файл `.env` рядом с `main.py`.

Пример:

```env
DB_TIME=postgresql+psycopg://postgres:postgres@localhost:5432/time_manager_db
SECRET_KEY=replace-with-a-long-random-secret-key
```

### Что означают переменные

- `DB_TIME` — строка подключения к базе данных PostgreSQL;
- `SECRET_KEY` — секрет для подписи JWT-токенов.

## Миграции

Перед первым запуском нужно создать таблицы через Alembic:

```bash
alembic upgrade head
```

Если нужно откатить последнюю миграцию:

```bash
alembic downgrade -1
```

## Запуск приложения

```bash
uvicorn main:app --reload
```

Документация Swagger:

- `http://127.0.0.1:8000/docs`

## Важный нюанс по `alembic.ini`

В `alembic.ini` не зашит конкретный URL базы данных.  
Это сделано специально: адрес БД подставляется из `.env` в файле `migrations/env.py`.

Такой подход удобнее и безопаснее:

- в репозиторий не попадают реальные данные подключения;
- проще переключаться между локальной БД и тестовой;
- настройка соответствует хорошей практике для учебных и рабочих проектов.

## Что нужно помнить

- приложение не создает таблицы автоматически;
- если миграции не выполнены, запросы к API не будут работать корректно;
- проект рассчитан в первую очередь на PostgreSQL;
- для локальных технических проверок можно временно использовать SQLite, но сдавать работу лучше с конфигурацией под PostgreSQL.
