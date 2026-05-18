"""Score leads according to how well they fit Ghar Ki Chai."""

from __future__ import annotations

import pandas as pd


SOUTH_EAST_LOCATIONS = (
    "london",
    "brighton",
    "oxford",
    "cambridge",
    "guildford",
    "reading",
    "sevenoaks",
    "tunbridge wells",
    "canterbury",
    "windsor",
    "kent",
    "surrey",
    "sussex",
    "berkshire",
    "hampshire",
)


def _contains_any(text: str, options: tuple[str, ...]) -> bool:
    return any(option in text.lower() for option in options)


def score_single_lead(row: dict, scoring_config: dict) -> dict:
    """Return score details for one lead row."""
    text = " ".join(str(row.get(field, "")) for field in ["category", "location", "business_name", "search_snippet", "notes"])
    text_lower = text.lower()
    score = int(scoring_config.get("base_score", 20))
    reasons: list[str] = []

    category = str(row.get("category", "")).lower()
    for configured_category, weight in scoring_config.get("category_weights", {}).items():
        if configured_category.lower() in category:
            score += int(weight)
            reasons.append(f"category fit: {configured_category}")
            break

    for keyword, weight in scoring_config.get("positive_keywords", {}).items():
        if keyword.lower() in text_lower:
            score += int(weight)
            reasons.append(f"positive keyword: {keyword}")

    for keyword, weight in scoring_config.get("negative_keywords", {}).items():
        if keyword.lower() in text_lower:
            score += int(weight)
            reasons.append(f"negative keyword: {keyword}")

    signals = scoring_config.get("signals", {})
    if row.get("emails"):
        score += int(signals.get("has_email", 0))
        reasons.append("email found")
    if row.get("contact_pages"):
        score += int(signals.get("has_contact_page", 0))
        reasons.append("contact page found")
    if row.get("instagram_links"):
        score += int(signals.get("has_instagram", 0))
        reasons.append("Instagram found")
    if row.get("website"):
        score += int(signals.get("has_website", 0))
        reasons.append("website found")
    if _contains_any(str(row.get("location", "")), SOUTH_EAST_LOCATIONS):
        score += int(signals.get("london_or_south_east", 0))
        reasons.append("target geography")

    score = max(0, min(100, score))
    return {"lead_score": score, "score_reasons": "; ".join(reasons)}


def score_leads(enriched_dataframe: pd.DataFrame, scoring_config: dict) -> pd.DataFrame:
    """Add score and reason columns to an enriched lead dataframe."""
    dataframe = enriched_dataframe.copy()
    score_rows = [score_single_lead(row.to_dict(), scoring_config) for _, row in dataframe.iterrows()]
    scores = pd.DataFrame(score_rows)
    dataframe = pd.concat([dataframe.reset_index(drop=True), scores], axis=1)
    return dataframe.sort_values(by="lead_score", ascending=False).reset_index(drop=True)
