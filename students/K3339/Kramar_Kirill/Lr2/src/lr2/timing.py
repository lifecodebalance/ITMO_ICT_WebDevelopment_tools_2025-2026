"""Helpers for benchmarking and table rendering."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class BenchmarkResult:
    approach: str
    seconds: float
    details: str = ""


def measure(function: Callable[..., T], *args, **kwargs) -> tuple[T, float]:
    started_at = perf_counter()
    result = function(*args, **kwargs)
    elapsed = perf_counter() - started_at
    return result, elapsed


def format_markdown_table(results: list[BenchmarkResult]) -> str:
    rows = ["| Подход | Время, сек | Комментарий |", "|---|---:|---|"]

    for item in results:
        rows.append(
            f"| {item.approach} | {item.seconds:.6f} | {item.details or '-'} |"
        )

    return "\n".join(rows)
