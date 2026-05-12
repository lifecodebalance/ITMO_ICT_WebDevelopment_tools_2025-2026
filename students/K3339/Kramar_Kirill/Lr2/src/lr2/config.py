"""Project configuration and shared constants for laboratory work 2."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal environments
    def load_dotenv() -> None:
        return None

# We load variables from .env in Lr2 first.
# If it is missing, python-dotenv silently keeps current environment variables.
load_dotenv()

SUM_UPPER_BOUND = 10_000_000_000_000
DEFAULT_WORKERS = max(2, os.cpu_count() or 2)

DEFAULT_URLS = [
    "https://example.com",
    "https://www.python.org",
    "https://docs.python.org/3/",
    "https://httpbin.org/html",
    "https://www.wikipedia.org",
    "https://github.com",
]

LAB_USER_USERNAME = "lab2_parser"
LAB_USER_EMAIL = "lab2_parser@example.com"
LAB_USER_PASSWORD_HASH = "not_used_in_lab2"

TASK_CATEGORY_NAME = "Parsed pages"
TASK_CATEGORY_COLOR = "#2A9D8F"

HTTP_TIMEOUT_SECONDS = 20
USER_AGENT = "ITMO-LR2-WebParser/1.0"


def get_database_url() -> str:
    """Return DB URL from environment.

    The assignment asks to use the database from laboratory work 1,
    where the same variable name `DB_TIME` is already used.
    """

    database_url = os.getenv("DB_TIME")
    if not database_url:
        raise RuntimeError(
            "DB_TIME is not set. Create .env in Lr2 or export DB_TIME in shell."
        )
    return database_url


def to_async_database_url(database_url: str) -> str:
    """Convert sync SQLAlchemy URL to async URL when needed."""

    if "+asyncpg" in database_url or "+aiosqlite" in database_url:
        return database_url

    if database_url.startswith("postgresql+psycopg://"):
        return database_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    if database_url.startswith("sqlite+pysqlite://"):
        return database_url.replace("sqlite+pysqlite://", "sqlite+aiosqlite://", 1)

    if database_url.startswith("sqlite://"):
        return database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    return database_url


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent
