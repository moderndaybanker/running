"""Visit prospect websites to extract contact details and useful notes."""

from __future__ import annotations

import logging
import os
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup

from utils import clean_text, extract_emails, extract_instagram_links, fetch_url, normalise_url, rate_limit


CONTACT_WORDS = ("contact", "wholesale", "stockist", "trade", "about")


def _safe_url(url: str) -> str:
    """Ensure a URL has a scheme before requests tries to fetch it."""
    if not url:
        return ""
    return url if url.startswith(("http://", "https://")) else f"https://{url}"


def _find_contact_pages(base_url: str, soup: BeautifulSoup) -> list[str]:
    """Find likely contact, wholesale, or about pages from a homepage."""
    pages: list[str] = []
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        label = clean_text(link.get_text(" ")).lower()
        combined = f"{href} {label}".lower()
        if any(word in combined for word in CONTACT_WORDS):
            pages.append(urljoin(base_url, href))
    return sorted(set(pages))[:5]


def enrich_single_lead(row: dict, timeout: int, user_agent: str, delay: float) -> dict:
    """Fetch a lead website and add contact signals."""
    website = _safe_url(str(row.get("website", "")))
    enriched = dict(row)
    enriched.update(
        {
            "emails": "",
            "instagram_links": "",
            "contact_pages": "",
            "notes": "",
            "enrichment_status": "skipped_no_website" if not website else "pending",
        }
    )

    if not website:
        return enriched

    try:
        logging.info("Enriching: %s", website)
        response = fetch_url(website, timeout=timeout, user_agent=user_agent)
        soup = BeautifulSoup(response.text, "html.parser")
        visible_text = clean_text(soup.get_text(" "))
        contact_pages = _find_contact_pages(website, soup)
        emails = set(extract_emails(response.text + " " + visible_text))
        instagram_links = set(extract_instagram_links(response.text))

        # Visit a small number of likely contact pages because emails often live there.
        for contact_page in contact_pages[:3]:
            rate_limit(delay)
            try:
                contact_response = fetch_url(contact_page, timeout=timeout, user_agent=user_agent)
                emails.update(extract_emails(contact_response.text))
                instagram_links.update(extract_instagram_links(contact_response.text))
            except Exception as exc:
                logging.warning("Could not fetch contact page %s: %s", contact_page, exc)

        enriched.update(
            {
                "business_name": row.get("business_name") or (soup.title.string if soup.title else ""),
                "emails": "; ".join(sorted(emails)),
                "instagram_links": "; ".join(sorted(instagram_links)),
                "contact_pages": "; ".join(contact_pages),
                "notes": visible_text[:500],
                "enrichment_status": "ok",
            }
        )
    except Exception as exc:
        logging.warning("Could not enrich %s: %s", website, exc)
        enriched["enrichment_status"] = f"error: {exc}"
    return enriched


def enrich_leads(raw_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Enrich and deduplicate raw lead rows."""
    timeout = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))
    delay = float(os.getenv("RATE_LIMIT_SECONDS", "2"))
    user_agent = os.getenv("USER_AGENT", "GharKiChaiOutreachBot/0.1")

    enriched_rows = []
    for _, row in raw_dataframe.iterrows():
        enriched_rows.append(enrich_single_lead(row.to_dict(), timeout=timeout, user_agent=user_agent, delay=delay))
        rate_limit(delay)

    dataframe = pd.DataFrame(enriched_rows)
    dataframe["dedupe_key"] = dataframe["website"].apply(normalise_url)
    dataframe = dataframe.sort_values(by=["emails", "contact_pages"], ascending=False)
    dataframe = dataframe.drop_duplicates(subset=["dedupe_key"], keep="first")
    return dataframe.reset_index(drop=True)
