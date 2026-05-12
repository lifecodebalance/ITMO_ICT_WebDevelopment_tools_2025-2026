"""Shared logic for task 1: summation with different concurrency approaches."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RangeChunk:
    start: int
    end: int


EXPECTED_SUM_UP_TO_10_13 = 50_000_000_000_005_000_000_000_000


def split_range_inclusive(start: int, end: int, parts: int) -> list[RangeChunk]:
    """Split [start, end] into approximately equal chunks."""

    if parts <= 0:
        raise ValueError("parts must be greater than zero")

    if end < start:
        return []

    total_numbers = end - start + 1
    base_size, remainder = divmod(total_numbers, parts)

    chunks: list[RangeChunk] = []
    current_start = start

    for index in range(parts):
        size = base_size + (1 if index < remainder else 0)
        current_end = current_start + size - 1

        if size > 0:
            chunks.append(RangeChunk(start=current_start, end=current_end))

        current_start = current_end + 1

    return chunks


def calculate_sum_for_range(start: int, end: int) -> int:
    """Calculate arithmetic progression sum for inclusive range [start, end]."""

    if end < start:
        return 0

    count = end - start + 1
    return (start + end) * count // 2


def expected_sum_to_n(n: int) -> int:
    """Classic formula: 1 + 2 + ... + n = n * (n + 1) // 2."""

    if n < 1:
        return 0
    return n * (n + 1) // 2
