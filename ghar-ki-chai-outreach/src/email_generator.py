"""Generate personalised outreach email drafts for human review."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils import clean_text, ensure_directory


def _first_name_or_default(row: dict) -> str:
    """Use a friendly generic greeting until a contact name is known."""
    return str(row.get("contact_name") or "there")


def _personalisation_points(row: dict) -> str:
    """Create short bullets from score reasons and scraped notes."""
    points = []
    if row.get("score_reasons"):
        points.extend(str(row["score_reasons"]).split("; ")[:3])
    if row.get("notes"):
        points.append(f"Website note: {clean_text(str(row['notes']))[:140]}")
    if not points:
        points.append("Your business appears aligned with premium, discovery-led products")
    return "\n".join(f"    - {point}" for point in points)


def _render_template(template: dict, row: dict) -> tuple[str, str]:
    values = {
        "business_name": row.get("business_name") or "your business",
        "contact_name": _first_name_or_default(row),
        "category": row.get("category") or "premium retail",
        "location": row.get("location") or "your area",
        "personalisation_points": _personalisation_points(row),
    }
    return template.get("subject", "").format(**values), template.get("body", "").format(**values)


def generate_email_drafts(scored_dataframe: pd.DataFrame, email_config: dict, output_dir: Path) -> pd.DataFrame:
    """Add email draft columns and save readable .txt drafts for top leads."""
    ensure_directory(output_dir)
    dataframe = scored_dataframe.copy()
    initial_template = email_config["initial_email"]
    follow_up_template = email_config["follow_up_email"]

    subjects = []
    bodies = []
    follow_up_subjects = []
    follow_up_bodies = []

    for index, row in dataframe.iterrows():
        row_dict = row.to_dict()
        subject, body = _render_template(initial_template, row_dict)
        follow_up_subject, follow_up_body = _render_template(follow_up_template, row_dict)
        subjects.append(subject)
        bodies.append(body)
        follow_up_subjects.append(follow_up_subject)
        follow_up_bodies.append(follow_up_body)

        safe_name = "".join(character if character.isalnum() else "_" for character in str(row_dict.get("business_name", f"lead_{index}")))[:60]
        draft_path = output_dir / f"{index + 1:03d}_{safe_name}.txt"
        draft_path.write_text(
            f"TO: {row_dict.get('emails', '')}\nSUBJECT: {subject}\n\n{body}\n\n--- FOLLOW UP ---\nSUBJECT: {follow_up_subject}\n\n{follow_up_body}",
            encoding="utf-8",
        )

    dataframe["email_subject"] = subjects
    dataframe["email_body"] = bodies
    dataframe["follow_up_subject"] = follow_up_subjects
    dataframe["follow_up_body"] = follow_up_bodies
    return dataframe
