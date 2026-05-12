# Лабораторная работа 2

Тема: потоки, процессы и асинхронность в Python.

Основной код находится в `src/lr2`, документация для MkDocs — в `docs/`.

Быстрый старт:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Запуск сравнения подходов:

```bash
PYTHONPATH=src python -m lr2.task1.run_benchmark
PYTHONPATH=src python -m lr2.task2.run_benchmark
```

Сборка документации:

```bash
mkdocs serve
```
