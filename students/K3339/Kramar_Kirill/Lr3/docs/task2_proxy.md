# Подзадача 2 — HTTP прокси

## Как это работает

```
Клиент → POST /parse?url=https://example.com → API (Lr1)
                                                    │
                                           POST /parse (JSON body)
                                                    │
                                                    ▼
                                           Parser-сервис (Lr2)
                                                    │
                                           возвращает {url, title}
                                                    │
                                                    ▼
                                           API сохраняет в БД ЛР1
                                                    │
                                           возвращает клиенту {url, title, saved_to_db}
```

## Новый файл: `Lr1/controllers/parser_proxy.py`

Добавлен роутер с префиксом `/parse`.

### `POST /parse`

```python
@router.post("", response_model=ParseResponse)
async def parse_url_sync(url: str, session: Session = Depends(get_session)):
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{PARSER_URL}/parse", json={"url": url})
        resp.raise_for_status()
        title = resp.json().get("title", "No title")
    _save_parsed_page(url, title, session)
    return ParseResponse(url=url, title=title, saved_to_db=True)
```

Используется `httpx.AsyncClient` — асинхронный HTTP-клиент. Это важно: FastAPI работает в event loop, и блокирующие вызовы (`requests.get(...)`) заблокировали бы весь сервер.

### Сохранение в БД

При первом вызове автоматически создаётся:
- пользователь `lr3_parser` (технический, без пароля)
- категория `Parsed pages (sync)` с зелёным цветом

Каждая спарсенная страница сохраняется как запись в таблицу `task` ЛР1.

### Почему парсер — отдельный сервис

- Разделение ответственности: API занимается бизнес-логикой, парсер — только HTML.
- Масштабируемость: парсер можно запустить в нескольких репликах независимо от API.
- Изоляция зависимостей: `requests`, `beautifulsoup4` не нужны в образе API.

## `PARSER_SERVICE_URL`

Адрес парсера передаётся через переменную окружения:

```yaml
# docker-compose.yml
environment:
  PARSER_SERVICE_URL: http://parser:8001
```

Для локального запуска без Docker нужно запустить парсер отдельно и задать:
```bash
export PARSER_SERVICE_URL=http://localhost:8001
```

## Parser API (`Lr2/parser_api.py`)

Минимальный FastAPI с одним эндпоинтом:

```python
@app.post("/parse", response_model=ParseResult)
def parse(req: ParseRequest) -> ParseResult:
    html_text = download_page_sync(req.url)     # из lr2.task2.parsing
    title = parse_title_from_html(html_text)    # BeautifulSoup
    return ParseResult(url=req.url, title=title)
```

Переиспользует функции из ЛР2 (`lr2.task2.parsing`) без дублирования кода.
