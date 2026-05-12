"""Run all task 2 approaches and print comparison table."""

from __future__ import annotations

import argparse

from lr2.config import DEFAULT_URLS, DEFAULT_WORKERS
from lr2.task2.async_parser import run_async_parser
from lr2.task2.multiprocessing_parser import run_multiprocessing_parser
from lr2.task2.threading_parser import run_threading_parser
from lr2.timing import BenchmarkResult, format_markdown_table


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare web parsing approaches")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--urls", nargs="*", default=DEFAULT_URLS)
    return parser


def main() -> None:
    args = build_parser().parse_args()

    threading_time = run_threading_parser(urls=args.urls, workers=args.workers)
    multiprocessing_time = run_multiprocessing_parser(urls=args.urls, workers=args.workers)
    async_time = run_async_parser(urls=args.urls, workers=args.workers)

    print("Итоги задачи 2")
    print(f"URL-адресов: {len(args.urls)}")
    print(f"Количество воркеров: {args.workers}")

    results = [
        BenchmarkResult("threading", threading_time),
        BenchmarkResult("multiprocessing", multiprocessing_time),
        BenchmarkResult("asyncio", async_time),
    ]

    print(format_markdown_table(results))


if __name__ == "__main__":
    main()
