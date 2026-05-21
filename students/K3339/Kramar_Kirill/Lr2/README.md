# Лабораторная работа 2

Тема: потоки, процессы и асинхронность в Python.

Основной код находится в `src/lr2`, документация для MkDocs — в `docs/`.

---

## Быстрый старт

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# отредактируйте .env — укажите DB_TIME от ЛР1
```

Запуск:

```bash
PYTHONPATH=src python -m lr2.task1.run_benchmark
PYTHONPATH=src python -m lr2.task2.run_benchmark
```

### Windows (Command Prompt)

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
rem отредактируйте .env — укажите DB_TIME от ЛР1
```

Запуск:

```cmd
set PYTHONPATH=src
python -m lr2.task1.run_benchmark
python -m lr2.task2.run_benchmark
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# отредактируйте .env — укажите DB_TIME от ЛР1
```

Запуск:

```powershell
$env:PYTHONPATH = "src"
python -m lr2.task1.run_benchmark
python -m lr2.task2.run_benchmark
```

---

## Сборка документации

```bash
mkdocs serve
```

Подробные инструкции — в [`docs/setup.md`](docs/setup.md).
