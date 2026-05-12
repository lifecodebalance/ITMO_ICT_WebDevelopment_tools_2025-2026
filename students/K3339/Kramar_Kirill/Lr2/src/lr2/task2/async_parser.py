"""Task 2: parallel parsing with asyncio + aiohttp."""

from __future__ import annotations

import argparse
import asyncio
import ssl

import aiohttp
import certifi

from lr2.config import DEFAULT_URLS, DEFAULT_WORKERS, USER_AGENT
from lr2.task2.db_async import StorageContext, prepare_storage_context, save_page_as_task
from lr2.task2.parsing import download_page_async, parse_title_from_html
from lr2.timing import measure

APPROACH_NAME = "asyncio"
_STORAGE_CONTEXT: StorageContext | None = None
_HTTP_SESSION: aiohttp.ClientSession | None = None


async def parse_and_save(url: str) -> None:
    """Required by assignment: download, parse and save one URL."""

    global _STORAGE_CONTEXT
    global _HTTP_SESSION

    if _STORAGE_CONTEXT is None:
        raise RuntimeError("Storage context is not initialized")
    if _HTTP_SESSION is None:
        raise RuntimeError("HTTP session is not initialized")

    try:
        html_text = await download_page_async(url, _HTTP_SESSION)
        title = parse_title_from_html(html_text)
    except Exception as error:
        title = f"ERROR: {type(error).__name__}"

    await save_page_as_task(
        url=url,
        title=title,
        approach=APPROACH_NAME,
        storage_context=_STORAGE_CONTEXT,
    )
    print(f"[{APPROACH_NAME}] {url} -> {title}")


async def run_async_parser_internal(urls: list[str], workers: int) -> None:
    global _STORAGE_CONTEXT
    global _HTTP_SESSION

    _STORAGE_CONTEXT = await prepare_storage_context(APPROACH_NAME)

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(limit=workers, ssl=ssl_context)
    timeout = aiohttp.ClientTimeout(total=None)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={"User-Agent": USER_AGENT},
    ) as session:
        _HTTP_SESSION = session

        semaphore = asyncio.Semaphore(workers)

        async def guarded_parse(url: str) -> None:
            async with semaphore:
                await parse_and_save(url)

        tasks = [asyncio.create_task(guarded_parse(url)) for url in urls]
        await asyncio.gather(*tasks)


def run_async_parser(urls: list[str], workers: int) -> float:
    def execute() -> None:
        asyncio.run(run_async_parser_internal(urls=urls, workers=workers))

    _, elapsed = measure(execute)
    return elapsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Asyncio web parser")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--urls", nargs="*", default=DEFAULT_URLS)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    elapsed = run_async_parser(urls=args.urls, workers=args.workers)

    print("Итоги parsing (asyncio)")
    print(f"URL-адресов: {len(args.urls)}")
    print(f"Асинхронных задач: {args.workers}")
    print(f"Время выполнения: {elapsed:.6f} сек")


if __name__ == "__main__":
    main()
