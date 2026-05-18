"""Generate search queries and collect raw lead results from pluggable providers."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Protocol

import requests

from utils import rate_limit


@dataclass
class SearchQuery:
    category: str
    location: str
    query: str


class SearchProvider(Protocol):
    """Interface every search provider must implement."""

    def search(self, query: str, limit: int) -> list[dict]:
        """Search the web and return raw result dictionaries."""


class MockSearchProvider:
    """Safe default provider that creates example rows without using an API."""

    def search(self, query: str, limit: int) -> list[dict]:
        return [
            {
                "title": f"Example prospect for {query}",
                "url": "https://example.com",
                "snippet": "Mock result. Set SEARCH_PROVIDER=serpapi or tavily in .env for live search.",
            }
        ][:limit]


class SerpApiSearchProvider:
    """Search provider backed by SerpAPI Google Search results."""

    endpoint = "https://serpapi.com/search.json"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("SERPAPI_API_KEY is required when using the serpapi provider.")
        self.api_key = api_key

    def search(self, query: str, limit: int) -> list[dict]:
        response = requests.get(
            self.endpoint,
            params={"engine": "google", "q": query, "api_key": self.api_key, "num": limit},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return [
            {"title": item.get("title", ""), "url": item.get("link", ""), "snippet": item.get("snippet", "")}
            for item in payload.get("organic_results", [])[:limit]
        ]


class TavilySearchProvider:
    """Search provider backed by Tavily's search API."""

    endpoint = "https://api.tavily.com/search"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("TAVILY_API_KEY is required when using the tavily provider.")
        self.api_key = api_key

    def search(self, query: str, limit: int) -> list[dict]:
        response = requests.post(
            self.endpoint,
            json={"api_key": self.api_key, "query": query, "max_results": limit},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return [
            {"title": item.get("title", ""), "url": item.get("url", ""), "snippet": item.get("content", "")}
            for item in payload.get("results", [])[:limit]
        ]


def build_search_provider(provider_name: str | None = None) -> SearchProvider:
    """Create the requested search provider from config or environment."""
    provider = (os.getenv("SEARCH_PROVIDER") or provider_name or "mock").lower()
    if provider == "serpapi":
        return SerpApiSearchProvider(os.getenv("SERPAPI_API_KEY", ""))
    if provider == "tavily":
        return TavilySearchProvider(os.getenv("TAVILY_API_KEY", ""))
    if provider != "mock":
        logging.warning("Unknown SEARCH_PROVIDER=%s; falling back to mock provider.", provider)
    return MockSearchProvider()


def generate_queries(search_config: dict) -> list[SearchQuery]:
    """Generate category/location search queries from config templates."""
    categories = search_config.get("categories", [])
    locations = search_config.get("locations", [])
    templates = search_config.get("query_templates", ["{category} {location}"])
    max_queries = int(search_config.get("search", {}).get("max_queries", 50))

    queries: list[SearchQuery] = []
    for category in categories:
        for location in locations:
            for template in templates:
                queries.append(SearchQuery(category=category, location=location, query=template.format(category=category, location=location)))
                if len(queries) >= max_queries:
                    return queries
    return queries


def research_leads(search_config: dict, provider: SearchProvider | None = None) -> list[dict]:
    """Run configured searches and return raw lead rows."""
    provider = provider or build_search_provider(search_config.get("search", {}).get("provider"))
    results_per_query = int(search_config.get("search", {}).get("results_per_query", 5))
    delay = float(search_config.get("search", {}).get("rate_limit_seconds", 2))

    rows: list[dict] = []
    for search_query in generate_queries(search_config):
        logging.info("Searching: %s", search_query.query)
        try:
            results = provider.search(search_query.query, results_per_query)
        except Exception as exc:  # Keep one failed query from stopping the workflow.
            logging.exception("Search failed for query '%s': %s", search_query.query, exc)
            continue

        for result in results:
            rows.append(
                {
                    "category": search_query.category,
                    "location": search_query.location,
                    "query": search_query.query,
                    "business_name": result.get("title", ""),
                    "website": result.get("url", ""),
                    "search_snippet": result.get("snippet", ""),
                }
            )
        rate_limit(delay)
    return rows
