"""Shared utilities for logging, rate limiting, CSV output, and text cleanup."""

from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import pandas as pd
import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
INSTAGRAM_PATTERN = re.compile(r"https?://(?:www\.)?instagram\.com/[A-Za-z0-9_.]+/?", re.I)


def setup_logging(level: str | None = None) -> None:
    """Configure console logging for non-engineer friendly progress messages."""
    logging.basicConfig(
        level=(level or os.getenv("LOG_LEVEL", "INFO")).upper(),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def rate_limit(seconds: float) -> None:
    """Sleep between network calls to avoid hammering websites or APIs."""
    if seconds > 0:
        time.sleep(seconds)


@retry(
    retry=retry_if_exception_type(requests.RequestException),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
)
def fetch_url(url: str, timeout: int, user_agent: str) -> requests.Response:
    """Fetch a URL with retries for transient network errors."""
    response = requests.get(url, timeout=timeout, headers={"User-Agent": user_agent})
    response.raise_for_status()
    return response


def ensure_directory(path: Path) -> None:
    """Create a directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def save_csv(rows: Iterable[dict], output_path: Path) -> Path:
    """Save rows to CSV, creating parent directories first."""
    ensure_directory(output_path.parent)
    dataframe = pd.DataFrame(list(rows))
    dataframe.to_csv(output_path, index=False)
    return output_path


def read_csv(path: Path) -> pd.DataFrame:
    """Read a CSV file, raising a clear error if it is missing."""
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(path).fillna("")


def clean_text(value: str) -> str:
    """Collapse whitespace so scraped snippets are easier to read."""
    return re.sub(r"\s+", " ", value or "").strip()


def normalise_url(url: str) -> str:
    """Normalise URLs for deduplication while keeping them human-readable."""
    if not url:
        return ""
    parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    return f"{host}{path}"


def extract_emails(text: str) -> list[str]:
    """Return unique email addresses found in text."""
    blocked_extensions = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")
    emails = sorted({email for email in EMAIL_PATTERN.findall(text or "") if not email.lower().endswith(blocked_extensions)})
    return emails


def extract_instagram_links(text: str) -> list[str]:
    """Return unique Instagram profile links found in text."""
    return sorted(set(INSTAGRAM_PATTERN.findall(text or "")))
