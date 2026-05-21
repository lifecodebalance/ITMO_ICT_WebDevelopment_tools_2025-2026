"""Celery application instance for Lr3.

Both the API service (to dispatch tasks) and the Celery worker (to execute them)
import this module.  It must remain import-side-effect-free so the FastAPI app
starts cleanly even when Redis is temporarily unavailable.
"""

from __future__ import annotations

import os

from celery import Celery

_broker = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "lr3",
    broker=_broker,
    backend=_backend,
    include=["celery_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
