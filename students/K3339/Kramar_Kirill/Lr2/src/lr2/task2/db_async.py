"""Asynchronous database access for task 2.

We intentionally use async SQLAlchemy here to satisfy the requirement
about asynchronous DB connection in the web labs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, insert, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from lr2.config import (
    LAB_USER_EMAIL,
    LAB_USER_PASSWORD_HASH,
    LAB_USER_USERNAME,
    TASK_CATEGORY_COLOR,
    TASK_CATEGORY_NAME,
    get_database_url,
    to_async_database_url,
)

metadata = MetaData()

user_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String),
    Column("email", String),
    Column("hashed_password", String),
    Column("created_at", DateTime),
)

task_category_table = Table(
    "taskcategory",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("color_code", String),
    Column("user_id", Integer),
)

task_table = Table(
    "task",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("description", String),
    Column("deadline", DateTime),
    Column("priority", String),
    Column("status", String),
    Column("estimated_time_minutes", Integer),
    Column("actual_time_minutes", Integer),
    Column("created_at", DateTime),
    Column("user_id", Integer),
    Column("category_id", Integer),
)


@dataclass(slots=True)
class StorageContext:
    user_id: int
    category_id: int


def _build_session_maker() -> tuple[async_sessionmaker[AsyncSession], object]:
    """Create async session factory and engine.

    NullPool is used to avoid cross-event-loop pool reuse issues when we run
    async code from threads or separate processes.
    """

    sync_url = get_database_url()
    async_url = to_async_database_url(sync_url)

    engine = create_async_engine(
        async_url,
        echo=False,
        pool_pre_ping=True,
        poolclass=NullPool,
    )
    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return session_maker, engine


async def _get_or_create_user(session: AsyncSession) -> int:
    user_query = select(user_table.c.id).where(user_table.c.username == LAB_USER_USERNAME)
    user_result = await session.execute(user_query)
    user_id = user_result.scalar_one_or_none()

    if user_id is not None:
        return int(user_id)

    insert_result = await session.execute(
        insert(user_table).values(
            username=LAB_USER_USERNAME,
            email=LAB_USER_EMAIL,
            hashed_password=LAB_USER_PASSWORD_HASH,
            created_at=datetime.utcnow(),
        )
    )

    inserted_id = insert_result.inserted_primary_key[0]
    if inserted_id is None:
        repeated_query = await session.execute(user_query)
        maybe_user_id = repeated_query.scalar_one_or_none()
        if maybe_user_id is None:
            raise RuntimeError("Could not create or fetch lab user")
        return int(maybe_user_id)

    return int(inserted_id)


async def _get_or_create_category(session: AsyncSession, user_id: int, approach: str) -> int:
    category_name = f"{TASK_CATEGORY_NAME} ({approach})"

    category_query = select(task_category_table.c.id).where(
        task_category_table.c.user_id == user_id,
        task_category_table.c.name == category_name,
    )
    category_result = await session.execute(category_query)
    category_id = category_result.scalar_one_or_none()

    if category_id is not None:
        return int(category_id)

    insert_result = await session.execute(
        insert(task_category_table).values(
            name=category_name,
            color_code=TASK_CATEGORY_COLOR,
            user_id=user_id,
        )
    )

    inserted_id = insert_result.inserted_primary_key[0]
    if inserted_id is None:
        repeated_query = await session.execute(category_query)
        maybe_category_id = repeated_query.scalar_one_or_none()
        if maybe_category_id is None:
            raise RuntimeError("Could not create or fetch parser category")
        return int(maybe_category_id)

    return int(inserted_id)


async def prepare_storage_context(approach: str) -> StorageContext:
    session_maker, engine = _build_session_maker()

    try:
        async with session_maker() as session:
            async with session.begin():
                user_id = await _get_or_create_user(session)
                category_id = await _get_or_create_category(session, user_id, approach)

            return StorageContext(user_id=user_id, category_id=category_id)
    finally:
        await engine.dispose()


async def save_page_as_task(
    *,
    url: str,
    title: str,
    approach: str,
    storage_context: StorageContext,
) -> None:
    session_maker, engine = _build_session_maker()

    try:
        async with session_maker() as session:
            async with session.begin():
                description = (
                    f"Страница: {url}\n"
                    f"Подход: {approach}\n"
                    f"Сохранено: {datetime.utcnow().isoformat()}"
                )

                await session.execute(
                    insert(task_table).values(
                        title=title[:250],
                        description=description,
                        deadline=None,
                        priority="medium",
                        status="todo",
                        estimated_time_minutes=5,
                        actual_time_minutes=0,
                        created_at=datetime.utcnow(),
                        user_id=storage_context.user_id,
                        category_id=storage_context.category_id,
                    )
                )
    finally:
        await engine.dispose()
