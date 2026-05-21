"""Lr3: endpoints that delegate parsing to the parser micro-service.

POST /parse          — synchronous call, waits for result, saves to DB.
POST /parse/async    — submits a Celery task, returns task_id immediately.
GET  /parse/async/{task_id} — polls Celery for status / result.
"""

from __future__ import annotations

import os
from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from celery_tasks import parse_url_task
from connection import get_session
from models import Task, TaskCategory, TaskPriority, TaskStatus, User

router = APIRouter(prefix="/parse", tags=["parser (Lr3)"])

PARSER_URL = os.getenv("PARSER_SERVICE_URL", "http://parser:8001")


# ---------------------------------------------------------------------------
# Internal DB helpers (create lr3_parser user + category on first call)
# ---------------------------------------------------------------------------

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
            TaskCategory.name == "Parsed pages (sync)",
        )
    ).first()
    if category:
        return category.id  # type: ignore[return-value]
    new_cat = TaskCategory(
        name="Parsed pages (sync)",
        color_code="#2A9D8F",
        user_id=user_id,
    )
    session.add(new_cat)
    session.commit()
    session.refresh(new_cat)
    return new_cat.id  # type: ignore[return-value]


def _save_parsed_page(url: str, title: str, session: Session) -> None:
    user_id = _get_or_create_parser_user(session)
    category_id = _get_or_create_category(session, user_id)
    task_record = Task(
        title=title[:250],
        description=(
            f"Parsed from: {url}\n"
            f"Approach: sync HTTP\n"
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


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class ParseResponse(BaseModel):
    url: str
    title: str
    saved_to_db: bool = False


class AsyncParseResponse(BaseModel):
    task_id: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=ParseResponse)
async def parse_url_sync(url: str, session: Session = Depends(get_session)) -> ParseResponse:
    """Call the parser service synchronously and persist the result."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{PARSER_URL}/parse", json={"url": url})
            resp.raise_for_status()
            title = resp.json().get("title", "No title")
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Parser service unavailable: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

    saved = False
    try:
        _save_parsed_page(url, title, session)
        saved = True
    except Exception:
        pass

    return ParseResponse(url=url, title=title, saved_to_db=saved)


@router.post("/async", response_model=AsyncParseResponse)
def parse_url_async(url: str) -> AsyncParseResponse:
    """Submit URL to the Celery queue. Returns task_id for polling."""
    task = parse_url_task.delay(url)
    return AsyncParseResponse(
        task_id=task.id,
        message=f"Task submitted. Poll status at GET /parse/async/{task.id}",
    )


@router.get("/async/{task_id}", response_model=TaskStatusResponse)
def get_parse_task_status(task_id: str) -> TaskStatusResponse:
    """Return the current status and result of a previously submitted task."""
    result = parse_url_task.AsyncResult(task_id)
    payload = None
    if result.ready():
        raw = result.result
        payload = raw if isinstance(raw, dict) else {"error": str(raw)}
    return TaskStatusResponse(task_id=task_id, status=result.status, result=payload)
