# Подзадача 3 — Celery

## Зачем очередь задач

Парсинг страниц — потенциально долгая операция (сеть медленная, страница большая).
Если держать HTTP-соединение клиента открытым на 10+ секунд — плохой UX и риск таймаута.

**Решение**: клиент отправляет URL, сразу получает `task_id`, и может проверить результат позже.
Тяжёлая работа выполняется фоновым воркером.

## Схема работы

```
1. Клиент → POST /parse/async?url=https://python.org
                 │
                 ▼
2. API → redis.rpush("lr3", task_payload)
   API ← {task_id: "abc-123", message: "Task submitted..."}
                 │
                 ▼
3. Celery worker берёт задачу из Redis
   worker → POST http://parser:8001/parse  (парсит страницу)
   worker → INSERT INTO task ...           (сохраняет в БД)
   worker → redis.set("celery-task-meta-abc-123", result)
                 │
                 ▼
4. Клиент → GET /parse/async/abc-123
   API ← redis.get("celery-task-meta-abc-123")
   Клиент ← {status: "SUCCESS", result: {url: "...", title: "..."}}
```

## Компоненты

### `Lr1/celery_app.py`

Определяет экземпляр Celery — брокер Redis, backend Redis.

```python
celery_app = Celery(
    "lr3",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["celery_tasks"],
)
```

### `Lr1/celery_tasks.py`

Определяет задачу `parse_url_task`:

```python
@celery_app.task(bind=True, max_retries=3)
def parse_url_task(self, url: str) -> dict:
    # 1. Вызвать parser-сервис
    response = httpx.post(f"{PARSER_URL}/parse", json={"url": url}, timeout=30)
    title = response.json().get("title", "No title")
    
    # 2. Сохранить в БД
    with Session(engine) as session:
        session.add(Task(title=title, ...))
        session.commit()
    
    return {"url": url, "title": title}
```

`bind=True` — задача получает ссылку на себя (`self`) для возможного `self.retry()`.
`max_retries=3` — автоматический повтор при ошибке.

### Эндпоинты в `parser_proxy.py`

**`POST /parse/async`** — отправляет задачу в очередь:
```python
task = parse_url_task.delay(url)   # .delay() — асинхронная отправка
return {"task_id": task.id, "message": "..."}
```

**`GET /parse/async/{task_id}`** — проверяет статус:
```python
result = parse_url_task.AsyncResult(task_id)
# result.status: PENDING | STARTED | SUCCESS | FAILURE
# result.result: итоговые данные (доступны когда SUCCESS)
```

### `celery_worker` в docker-compose.yml

```yaml
celery_worker:
  build:
    context: ../Lr1
    dockerfile: Dockerfile      # тот же образ, что и у API
  command: celery -A celery_app worker --loglevel=info --concurrency=2
```

Воркер — это тот же Docker-образ, что и API, но запущенный с командой `celery ... worker` вместо `uvicorn`.

## Возможные статусы задачи

| Статус | Описание |
|---|---|
| `PENDING` | Задача в очереди, воркер ещё не взял её |
| `STARTED` | Воркер начал выполнение |
| `SUCCESS` | Задача завершена, результат доступен |
| `FAILURE` | Ошибка при выполнении |
| `RETRY` | Задача перезапускается после ошибки |

## Почему Redis, а не RabbitMQ

Redis проще в настройке для учебных целей — один контейнер, нет сложного конфига.
В production чаще используют RabbitMQ как брокер (надёжнее гарантии доставки), но для сохранения результатов Redis остаётся стандартом.
