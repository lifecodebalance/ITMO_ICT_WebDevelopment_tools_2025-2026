"""Celery task definitions for Lr3.

The worker runs this module.  It calls the parser service over HTTP,
then saves the result into the Lr1 database.
"""

from __future__ import annotations

import os
from datetime import datetime

import httpx
from sqlmodel import Session, select

from celery_app import celery_app
from connection import engine
from models import Task, TaskCategory, TaskPriority, TaskStatus, User

PARSER_URL = os.getenv("PARSER_SERVICE_URL", "http://parser:8001")


def _get_or_create_parser_user(session: Session) -> int:
    user = session.exec(select(User).where(User.username == "lr3_parser")).first()
    if user:
        return user.id  # type: ignore[return-value]
    new_user = User(
        username="lr3_parser",
        email="lr3_parser@example.com",
        hashed_password="not_used_in_lr3",
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user.id  # type: ignore[return-value]


def _get_or_create_category(session: Session, user_id: int) -> int:
    category = session.exec(
        select(TaskCategory).where(
            TaskCategory.user_id == user_id,
            TaskCategory.name == "Parsed pages (celery)",
        )
    ).first()
    if category:
        return category.id  # type: ignore[return-value]
    new_cat = TaskCategory(
        name="Parsed pages (celery)",
        color_code="#E76F51",
        user_id=user_id,
    )
    session.add(new_cat)
    session.commit()
    session.refresh(new_cat)
    return new_cat.id  # type: ignore[return-value]


@celery_app.task(bind=True, max_retries=3)
def parse_url_task(self, url: str) -> dict:  # type: ignore[override]
    """Call the parser service, save result to DB, return {url, title}."""
    try:
        response = httpx.post(f"{PARSER_URL}/parse", json={"url": url}, timeout=30)
        response.raise_for_status()
        title = response.json().get("title", "No title")
    except Exception as exc:
        title = f"ERROR: {type(exc).__name__}: {exc}"

    try:
        with Session(engine) as session:
            user_id = _get_or_create_parser_user(session)
            category_id = _get_or_create_category(session, user_id)
            task_record = Task(
                title=title[:250],
                description=(
                    f"Parsed from: {url}\n"
                    f"Approach: celery\n"
                    f"At: {datetime.utcnow().isoformat()}"
                ),
                priority=TaskPriority.medium,
                status=TaskStatus.todo,
                estimated_time_minutes=5,
                actual_time_minutes=0,
                user_id=user_id,
                category_id=category_id,
            )
            session.add(task_record)
            session.commit()
    except Exception:
        pass  # DB save is best-effort; don't fail the task

    return {"url": url, "title": title}
