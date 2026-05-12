"""Shared helpers for task 2."""

from __future__ import annotations


def split_urls_evenly(urls: list[str], parts: int) -> list[list[str]]:
    if parts <= 0:
        raise ValueError("parts must be > 0")

    if not urls:
        return []

    base_size, remainder = divmod(len(urls), parts)
    chunks: list[list[str]] = []
    start_index = 0

    for index in range(parts):
        current_size = base_size + (1 if index < remainder else 0)
        end_index = start_index + current_size

        if current_size > 0:
            chunks.append(urls[start_index:end_index])

        start_index = end_index

    return chunks
