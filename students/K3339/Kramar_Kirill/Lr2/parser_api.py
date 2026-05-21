"""Minimal FastAPI service that exposes the Lr2 parser over HTTP.

This is the entry-point for the `parser` Docker container used in Lr3.
It does NOT connect to a database — it only downloads pages and extracts titles.
The API service (Lr1) is responsible for persisting results.
"""

from __future__ import annotations

import sys
import os

# Make the lr2 package importable inside the container (src/ layout)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI
from pydantic import BaseModel

from lr2.task2.parsing import download_page_sync, parse_title_from_html

app = FastAPI(
    title="Parser Service",
    description="Web-page title extractor for Lr3 (called by the API service).",
    version="1.0.0",
)


class ParseRequest(BaseModel):
    url: str


class ParseResult(BaseModel):
    url: str
    title: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/parse", response_model=ParseResult)
def parse(req: ParseRequest) -> ParseResult:
    """Download the page at `url` and return its <title>."""
    try:
        html_text = download_page_sync(req.url)
        title = parse_title_from_html(html_text)
    except Exception as exc:
        title = f"ERROR: {type(exc).__name__}: {exc}"
    return ParseResult(url=req.url, title=title)
