"""Task 1: summation with the threading module."""

from __future__ import annotations

import argparse
from threading import Thread

from lr2.config import DEFAULT_WORKERS, SUM_UPPER_BOUND
from lr2.task1.common import RangeChunk, calculate_sum_for_range, expected_sum_to_n, split_range_inclusive
from lr2.timing import measure


def calculate_sum(chunk: RangeChunk) -> int:
    """Required function for the assignment: sum values for one chunk."""

    return calculate_sum_for_range(chunk.start, chunk.end)


def _thread_worker(index: int, chunk: RangeChunk, partial_results: list[int]) -> None:
    partial_results[index] = calculate_sum(chunk)


def run_threading_sum(upper_bound: int = SUM_UPPER_BOUND, workers: int = DEFAULT_WORKERS) -> tuple[int, float]:
    chunks = split_range_inclusive(start=1, end=upper_bound, parts=workers)
    partial_results = [0] * len(chunks)
    threads: list[Thread] = []

    def execute() -> int:
        for index, chunk in enumerate(chunks):
            thread = Thread(target=_thread_worker, args=(index, chunk, partial_results))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        return sum(partial_results)

    total_sum, elapsed = measure(execute)
    return total_sum, elapsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Threading summation benchmark")
    parser.add_argument("--upper-bound", type=int, default=SUM_UPPER_BOUND)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    total_sum, elapsed = run_threading_sum(
        upper_bound=args.upper_bound,
        workers=args.workers,
    )
    expected_value = expected_sum_to_n(args.upper_bound)

    print(f"Подход: threading")
    print(f"Диапазон: 1..{args.upper_bound}")
    print(f"Потоки: {args.workers}")
    print(f"Сумма: {total_sum}")
    print(f"Ожидаемое значение: {expected_value}")
    print(f"Совпадает: {total_sum == expected_value}")
    print(f"Время выполнения: {elapsed:.6f} сек")


if __name__ == "__main__":
    main()
