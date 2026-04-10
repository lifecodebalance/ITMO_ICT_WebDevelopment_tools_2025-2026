# Time Manager API

Учебный серверный проект на FastAPI для лабораторной работы.  
Приложение реализует простой тайм-менеджер: пользователь может регистрироваться, создавать задачи, объединять их по категориям, помечать тегами и добавлять напоминания.

## Что умеет проект

- регистрация и вход пользователя;
- генерация JWT-токена;
- аутентификация по `Bearer`-токену;
- хэширование паролей;
- CRUD для задач и категорий;
- CRUD для тегов;
- CRUD для напоминаний;
- получение подробной информации о пользователе и его данных;
- работа с миграциями через Alembic;
- хранение конфигурации подключения к БД в переменных окружения.

## Предметная область

Проект действительно реализует **тайм-менеджер**.

Основная сущность здесь `Task`:

- у задачи есть название и описание;
- можно указать дедлайн;
- можно задавать приоритет и статус;
- можно хранить ожидаемое и фактическое время;
- задачу можно отнести к категории;
- задачу можно связать с несколькими тегами;
- для задачи можно создать несколько напоминаний.

## Структура данных

В проекте используются 6 таблиц:

1. `user` — пользователи.
2. `task` — задачи.
3. `taskcategory` — категории задач.
4. `tag` — теги.
5. `tasktag` — ассоциативная таблица между задачами и тегами.
6. `reminder` — напоминания.

Связи:

- `user -> task` — one-to-many;
- `user -> taskcategory` — one-to-many;
- `user -> tag` — one-to-many;
- `task -> reminder` — one-to-many;
- `task <-> tag` — many-to-many через `tasktag`.

В `tasktag` есть не только внешние ключи, но и дополнительные поля:

- `added_at` — когда тег был добавлен к задаче;
- `is_primary` — основной ли это тег для задачи.

## Запуск проекта

### 1. Установить зависимости

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

### 2. Подготовить `.env`

Создайте файл `.env` рядом с `main.py` и заполните по примеру `.env.example`:

```env
DB_TIME=postgresql+psycopg://postgres:postgres@localhost:5432/time_manager_db
SECRET_KEY=replace-with-a-long-random-secret-key
```

### 3. Выполнить миграции

```bash
alembic upgrade head
```

### 4. Запустить сервер

```bash
uvicorn main:app --reload
```

После запуска документация Swagger будет доступна по адресу:

- `http://127.0.0.1:8000/docs`

## Важный нюанс по Alembic

Строка подключения к базе **не хранится напрямую в `alembic.ini`**.  
Она берется из переменной окружения `DB_TIME` внутри файла `migrations/env.py`.

Это как раз тот момент, о котором тебе сказала коллега: секреты и конкретный URL БД лучше не оставлять в `alembic.ini`, а подставлять из `.env`.

## Что уже реализовано корректно

- проект разбит по модулям: `auth`, `controllers`, `migrations`;
- ответы пользователя больше не возвращают `hashed_password`;
- регистрация не падает при проверке дубликатов;
- миграция действительно создает таблицы;
- `PATCH` для категории теперь работает как частичное обновление;
- добавлены недостающие обновления для тегов и напоминаний;
- доступ к подробным данным пользователя ограничен его собственным профилем.

## Нюансы

- приложение не создает таблицы автоматически при старте;
- перед запуском нужно выполнить `alembic upgrade head`;
- список пользователей доступен авторизованному пользователю, но без чувствительных данных;
- подробные данные по пользователю доступны только владельцу профиля;
- Вообще можно делать PostgreSQL, но тестилось все только с SQLite.

## Краткий список основных маршрутов

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `PATCH /auth/password`

### Users

- `GET /users/`
- `GET /users/{user_id}`
- `GET /users/me/details`
- `GET /users/{user_id}/details`

### Tasks

- `POST /tasks/`
- `GET /tasks/`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `POST /tasks/{task_id}/tags/{tag_id}`
- `DELETE /tasks/{task_id}/tags/{tag_id}`

### Categories

- `POST /categories/`
- `GET /categories/`
- `GET /categories/{category_id}`
- `PATCH /categories/{category_id}`
- `DELETE /categories/{category_id}`

### Tags

- `POST /tags/`
- `GET /tags/`
- `GET /tags/{tag_id}`
- `PATCH /tags/{tag_id}`
- `DELETE /tags/{tag_id}`

### Reminders

- `POST /reminders/`
- `GET /reminders/`
- `GET /reminders/{reminder_id}`
- `PATCH /reminders/{reminder_id}`
- `DELETE /reminders/{reminder_id}`

## Документация для GitHub Pages

В папке [`docs/`](../docs) лежит подробная документация для публикации через GitHub Pages:

- [Главная страница](../index.md)
- [Запуск проекта](../run-guide.md)
- [Описание API](../api.md)
- [Модель данных](../data-model.md)
