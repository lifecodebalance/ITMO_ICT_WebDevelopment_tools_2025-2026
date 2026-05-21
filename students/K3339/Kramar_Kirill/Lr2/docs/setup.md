# Подготовка и запуск

## Требования

- Python 3.11 или новее
- PostgreSQL (или любая другая СУБД из ЛР1)
- Выполненные и применённые миграции ЛР1 (таблицы `user`, `taskcategory`, `task` должны существовать)

---

## 1. Создание виртуального окружения и установка зависимостей

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (Command Prompt)

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Если PowerShell ругается на политику выполнения скриптов, выполните один раз:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## 2. Настройка `.env`

Скопируйте пример конфигурации:

### macOS / Linux

```bash
cp .env.example .env
```

### Windows (Command Prompt)

```cmd
copy .env.example .env
```

### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
```

Откройте `.env` и укажите строку подключения к БД из ЛР1:

```env
DB_TIME=postgresql+psycopg://postgres:postgres@localhost:5432/time_manager_db
```

Если в ЛР1 использовался SQLite:

```env
DB_TIME=sqlite:///../Lr1/time_manager.db
```

---

## 3. Подготовка схемы БД

ЛР2 пишет в таблицы ЛР1 (`user`, `taskcategory`, `task`). Они должны существовать.

Если вы ещё не применяли миграции ЛР1 — перейдите в папку ЛР1 и выполните:

```bash
alembic upgrade head
```

---

## 4. Запуск задачи 1 (сравнение подходов для суммы)

### macOS / Linux

```bash
PYTHONPATH=src python -m lr2.task1.run_benchmark
```

С параметрами (например, 4 воркера):

```bash
PYTHONPATH=src python -m lr2.task1.run_benchmark --workers 4
```

Отдельные варианты:

```bash
PYTHONPATH=src python -m lr2.task1.threading_sum
PYTHONPATH=src python -m lr2.task1.multiprocessing_sum
PYTHONPATH=src python -m lr2.task1.async_sum
```

### Windows (Command Prompt)

```cmd
set PYTHONPATH=src
python -m lr2.task1.run_benchmark
```

С параметрами:

```cmd
set PYTHONPATH=src
python -m lr2.task1.run_benchmark --workers 4
```

Отдельные варианты:

```cmd
set PYTHONPATH=src
python -m lr2.task1.threading_sum
python -m lr2.task1.multiprocessing_sum
python -m lr2.task1.async_sum
```

### Windows (PowerShell)

```powershell
$env:PYTHONPATH = "src"
python -m lr2.task1.run_benchmark
```

С параметрами:

```powershell
$env:PYTHONPATH = "src"
python -m lr2.task1.run_benchmark --workers 4
```

---

## 5. Запуск задачи 2 (парсинг + запись в БД)

### macOS / Linux

```bash
PYTHONPATH=src python -m lr2.task2.run_benchmark
```

С параметрами:

```bash
PYTHONPATH=src python -m lr2.task2.run_benchmark --workers 3
```

Отдельные варианты:

```bash
PYTHONPATH=src python -m lr2.task2.threading_parser
PYTHONPATH=src python -m lr2.task2.multiprocessing_parser
PYTHONPATH=src python -m lr2.task2.async_parser
```

### Windows (Command Prompt)

```cmd
set PYTHONPATH=src
python -m lr2.task2.run_benchmark
```

С параметрами:

```cmd
set PYTHONPATH=src
python -m lr2.task2.run_benchmark --workers 3
```

Отдельные варианты:

```cmd
set PYTHONPATH=src
python -m lr2.task2.threading_parser
python -m lr2.task2.multiprocessing_parser
python -m lr2.task2.async_parser
```

### Windows (PowerShell)

```powershell
$env:PYTHONPATH = "src"
python -m lr2.task2.run_benchmark
```

---

## 6. Сборка документации

```bash
mkdocs serve
```

Откройте в браузере: `http://127.0.0.1:8000`

---

## Технические нюансы

- На **Windows** в `multiprocessing` используется механизм `spawn` (не `fork`), поэтому важна защита `if __name__ == "__main__"` в каждом запускаемом файле — она уже добавлена. `freeze_support()` также вызывается в нужных местах.
- Для `aiohttp` добавлен явный SSL-контекст через `certifi` — это исключает ошибки с сертификатами на Windows и macOS при HTTPS-запросах.
- Для async SQLAlchemy нужен `greenlet` — он добавлен в `requirements.txt`.
- Переменная `PYTHONPATH=src` нужна, чтобы Python находил пакет `lr2` в папке `src/`. Как только окружение активировано — устанавливать её достаточно один раз на сессию терминала.
