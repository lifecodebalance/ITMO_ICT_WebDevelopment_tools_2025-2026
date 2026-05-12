"""Task 1: summation with asyncio."""

from __future__ import annotations

import argparse
import asyncio

from lr2.config import DEFAULT_WORKERS, SUM_UPPER_BOUND
from lr2.task1.common import RangeChunk, calculate_sum_for_range, expected_sum_to_n, split_range_inclusive
from lr2.timing import measure


async def calculate_sum(chunk: RangeChunk) -> int:
    """Required function for the assignment: async chunk sum."""

    return await asyncio.to_thread(calculate_sum_for_range, chunk.start, chunk.end)


async def run_async_sum_internal(upper_bound: int, workers: int) -> int:
    chunks = split_range_inclusive(start=1, end=upper_bound, parts=workers)
    tasks = [asyncio.create_task(calculate_sum(chunk)) for chunk in chunks]
    partial_results = await asyncio.gather(*tasks)
    return sum(partial_results)


def run_async_sum(upper_bound: int = SUM_UPPER_BOUND, workers: int = DEFAULT_WORKERS) -> tuple[int, float]:
    def execute() -> int:
        return asyncio.run(run_async_sum_internal(upper_bound=upper_bound, workers=workers))

    total_sum, elapsed = measure(execute)
    return total_sum, elapsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Asyncio summation benchmark")
    parser.add_argument("--upper-bound", type=int, default=SUM_UPPER_BOUND)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    total_sum, elapsed = run_async_sum(
        upper_bound=args.upper_bound,
        workers=args.workers,
    )
    expected_value = expected_sum_to_n(args.upper_bound)

    print("Подход: asyncio")
    print(f"Диапазон: 1..{args.upper_bound}")
    print(f"Асинхронных задач: {args.workers}")
    print(f"Сумма: {total_sum}")
    print(f"Ожидаемое значение: {expected_value}")
    print(f"Совпадает: {total_sum == expected_value}")
    print(f"Время выполнения: {elapsed:.6f} сек")


if __name__ == "__main__":
    main()
