"""Task 2: parallel parsing with multiprocessing."""

from __future__ import annotations

import argparse
import asyncio
from multiprocessing import Pool, freeze_support

from lr2.config import DEFAULT_URLS, DEFAULT_WORKERS
from lr2.task2.common import split_urls_evenly
from lr2.task2.db_async import StorageContext, prepare_storage_context, save_page_as_task
from lr2.task2.parsing import download_page_sync, parse_title_from_html
from lr2.timing import measure

APPROACH_NAME = "multiprocessing"
_STORAGE_CONTEXT: StorageContext | None = None


def _init_worker(storage_context: StorageContext) -> None:
    global _STORAGE_CONTEXT
    _STORAGE_CONTEXT = storage_context


def parse_and_save(url: str) -> None:
    """Required by assignment: download, parse and save one URL."""

    global _STORAGE_CONTEXT

    if _STORAGE_CONTEXT is None:
        raise RuntimeError("Storage context is not initialized")

    try:
        html_text = download_page_sync(url)
        title = parse_title_from_html(html_text)
    except Exception as error:
        title = f"ERROR: {type(error).__name__}"

    asyncio.run(
        save_page_as_task(
            url=url,
            title=title,
            approach=APPROACH_NAME,
            storage_context=_STORAGE_CONTEXT,
        )
    )
    print(f"[{APPROACH_NAME}] {url} -> {title}")


def _process_chunk(url_chunk: list[str]) -> None:
    for url in url_chunk:
        parse_and_save(url)


def run_multiprocessing_parser(urls: list[str], workers: int) -> float:
    storage_context = asyncio.run(prepare_storage_context(APPROACH_NAME))
    url_chunks = split_urls_evenly(urls, workers)

    def execute() -> None:
        with Pool(
            processes=workers,
            initializer=_init_worker,
            initargs=(storage_context,),
        ) as pool:
            pool.map(_process_chunk, url_chunks)

    _, elapsed = measure(execute)
    return elapsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Multiprocessing web parser with async DB writes"
    )
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--urls", nargs="*", default=DEFAULT_URLS)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    elapsed = run_multiprocessing_parser(urls=args.urls, workers=args.workers)

    print("Итоги parsing (multiprocessing)")
    print(f"URL-адресов: {len(args.urls)}")
    print(f"Процессов: {args.workers}")
    print(f"Время выполнения: {elapsed:.6f} сек")


if __name__ == "__main__":
    freeze_support()
    main()
