"""HTML downloading and title parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass

import aiohttp
import requests
from bs4 import BeautifulSoup

from lr2.config import HTTP_TIMEOUT_SECONDS, USER_AGENT


@dataclass(slots=True)
class ParsedPage:
    url: str
    title: str


def parse_title_from_html(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "html.parser")
    title_tag = soup.find("title")

    if title_tag is None:
        return "No <title> found"

    title_text = title_tag.get_text(strip=True)
    return title_text or "Empty <title>"


def download_page_sync(url: str) -> str:
    response = requests.get(
        url,
        timeout=HTTP_TIMEOUT_SECONDS,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response.text


async def download_page_async(url: str, session: aiohttp.ClientSession) -> str:
    async with session.get(url, timeout=HTTP_TIMEOUT_SECONDS) as response:
        response.raise_for_status()
        return await response.text()
