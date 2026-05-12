"""Run all task 1 approaches and print comparison table."""

from __future__ import annotations

import argparse

from lr2.config import DEFAULT_WORKERS, SUM_UPPER_BOUND
from lr2.task1.async_sum import run_async_sum
from lr2.task1.multiprocessing_sum import run_multiprocessing_sum
from lr2.task1.threading_sum import run_threading_sum
from lr2.timing import BenchmarkResult, format_markdown_table


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare threading, multiprocessing and asyncio")
    parser.add_argument("--upper-bound", type=int, default=SUM_UPPER_BOUND)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    return parser


def main() -> None:
    args = build_parser().parse_args()

    threading_sum, threading_time = run_threading_sum(
        upper_bound=args.upper_bound,
        workers=args.workers,
    )
    multiprocessing_sum, multiprocessing_time = run_multiprocessing_sum(
        upper_bound=args.upper_bound,
        workers=args.workers,
    )
    async_sum, async_time = run_async_sum(
        upper_bound=args.upper_bound,
        workers=args.workers,
    )

    print("Итоги задачи 1")
    print(f"Диапазон: 1..{args.upper_bound}")
    print(f"Количество воркеров: {args.workers}")
    print(f"Проверка равенства сумм: {threading_sum == multiprocessing_sum == async_sum}")

    results = [
        BenchmarkResult("threading", threading_time),
        BenchmarkResult("multiprocessing", multiprocessing_time),
        BenchmarkResult("asyncio", async_time),
    ]

    print(format_markdown_table(results))


if __name__ == "__main__":
    main()
