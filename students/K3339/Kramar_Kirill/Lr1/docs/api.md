# Описание API

## Аутентификация

После входа пользователь получает JWT-токен.  
Его нужно передавать в заголовке:

```http
Authorization: Bearer <token>
```

## Auth

### `POST /auth/register`

Создает нового пользователя.

Пример тела:

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "strong-password"
}
```

### `POST /auth/login`

Проверяет логин и пароль, возвращает JWT.

### `GET /auth/me`

Возвращает безопасную информацию о текущем пользователе:

- `id`
- `username`
- `email`
- `created_at`

### `PATCH /auth/password`

Меняет пароль текущего пользователя.

## Users

### `GET /users/`

Возвращает список пользователей без чувствительных данных.

### `GET /users/{user_id}`

Возвращает данные пользователя по id.  
В текущей версии доступно только владельцу этого профиля.

### `GET /users/me/details`

Возвращает подробную информацию о текущем пользователе:

- базовые данные профиля;
- задачи;
- категории;
- теги;
- напоминания.

### `GET /users/{user_id}/details`

Тот же подробный профиль, но по id.  
Тоже доступен только владельцу.

## Tasks

### `POST /tasks/`

Создает задачу.

Основные поля:

- `title`
- `description`
- `deadline`
- `priority`
- `status`
- `estimated_time_minutes`
- `actual_time_minutes`
- `category_id`

### `GET /tasks/`

Возвращает список задач текущего пользователя вместе с вложенными тегами.

### `GET /tasks/{task_id}`

Возвращает одну задачу вместе с тегами.

### `PATCH /tasks/{task_id}`

Частично обновляет задачу.

### `DELETE /tasks/{task_id}`

Удаляет задачу.

### `POST /tasks/{task_id}/tags/{tag_id}`

Привязывает тег к задаче.  
Поддерживает query-параметр `is_primary`.

### `DELETE /tasks/{task_id}/tags/{tag_id}`

Убирает тег у задачи.

## Categories

### `POST /categories/`

Создает категорию.

### `GET /categories/`

Возвращает список категорий текущего пользователя.

### `GET /categories/{category_id}`

Возвращает категорию по id.

### `PATCH /categories/{category_id}`

Частично обновляет категорию.

### `DELETE /categories/{category_id}`

Удаляет категорию.

## Tags

### `POST /tags/`

Создает тег.

### `GET /tags/`

Возвращает список тегов текущего пользователя.

### `GET /tags/{tag_id}`

Возвращает тег по id.

### `PATCH /tags/{tag_id}`

Частично обновляет тег.

### `DELETE /tags/{tag_id}`

Удаляет тег.

## Reminders

### `POST /reminders/`

Создает напоминание для задачи.

### `GET /reminders/`

Возвращает список напоминаний текущего пользователя.

### `GET /reminders/{reminder_id}`

Возвращает одно напоминание.

### `PATCH /reminders/{reminder_id}`

Частично обновляет напоминание.

### `DELETE /reminders/{reminder_id}`

Удаляет напоминание.
