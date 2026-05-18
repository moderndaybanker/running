"""Command line entry point for the Ghar Ki Chai outreach workflow."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path

from config_loader import PROJECT_ROOT, load_environment, load_yaml_config
from email_generator import generate_email_drafts
from lead_enricher import enrich_leads
from lead_researcher import research_leads
from lead_scorer import score_leads
from utils import read_csv, save_csv, setup_logging


def timestamp() -> str:
    """Return a filesystem-friendly timestamp for output files."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def build_parser() -> argparse.ArgumentParser:
    """Create the command line parser."""
    parser = argparse.ArgumentParser(description="Find, enrich, score, and draft outreach for Ghar Ki Chai prospects.")
    parser.add_argument(
        "command",
        choices=["research", "enrich", "score", "emails", "run-all"],
        help="Workflow step to run. Use run-all for the full workflow.",
    )
    parser.add_argument("--raw-csv", type=Path, help="Existing raw CSV to enrich.")
    parser.add_argument("--enriched-csv", type=Path, help="Existing enriched CSV to score.")
    parser.add_argument("--scored-csv", type=Path, help="Existing scored CSV to generate emails from.")
    return parser


def run_research(search_config: dict) -> Path:
    rows = research_leads(search_config)
    configured_output = search_config.get("settings", {}).get("output_raw_file")
    output_path = (
        PROJECT_ROOT / configured_output
        if configured_output
        else PROJECT_ROOT / "data" / "raw" / f"raw_leads_{timestamp()}.csv"
    )
    save_csv(rows, output_path)
    logging.info("Saved %s raw leads to %s", len(rows), output_path)
    return output_path


def run_enrich(raw_csv: Path) -> Path:
    raw_dataframe = read_csv(raw_csv)
    enriched_dataframe = enrich_leads(raw_dataframe)
    output_path = PROJECT_ROOT / "data" / "enriched" / f"enriched_leads_{timestamp()}.csv"
    enriched_dataframe.to_csv(output_path, index=False)
    logging.info("Saved %s enriched leads to %s", len(enriched_dataframe), output_path)
    return output_path


def run_score(enriched_csv: Path, scoring_config: dict) -> Path:
    enriched_dataframe = read_csv(enriched_csv)
    scored_dataframe = score_leads(enriched_dataframe, scoring_config)
    output_path = PROJECT_ROOT / "data" / "final" / f"scored_leads_{timestamp()}.csv"
    scored_dataframe.to_csv(output_path, index=False)
    logging.info("Saved %s scored leads to %s", len(scored_dataframe), output_path)
    return output_path


def run_emails(scored_csv: Path, email_config: dict) -> Path:
    scored_dataframe = read_csv(scored_csv)
    final_dataframe = generate_email_drafts(scored_dataframe, email_config, PROJECT_ROOT / "outputs" / "emails")
    output_path = PROJECT_ROOT / "data" / "final" / f"final_outreach_{timestamp()}.csv"
    final_dataframe.to_csv(output_path, index=False)
    logging.info("Saved final outreach CSV to %s", output_path)
    logging.info("Email drafts were saved for review only. No emails were sent.")
    return output_path


def main() -> None:
    load_environment()
    setup_logging()
    args = build_parser().parse_args()

    search_config = load_yaml_config("search_config.yaml")
    scoring_config = load_yaml_config("scoring_config.yaml")
    email_config = load_yaml_config("email_templates.yaml")

    if args.command == "research":
        run_research(search_config)
    elif args.command == "enrich":
        if not args.raw_csv:
            raise SystemExit("--raw-csv is required for enrich")
        run_enrich(args.raw_csv)
    elif args.command == "score":
        if not args.enriched_csv:
            raise SystemExit("--enriched-csv is required for score")
        run_score(args.enriched_csv, scoring_config)
    elif args.command == "emails":
        if not args.scored_csv:
            raise SystemExit("--scored-csv is required for emails")
        run_emails(args.scored_csv, email_config)
    elif args.command == "run-all":
        raw_csv = run_research(search_config)
        enriched_csv = run_enrich(raw_csv)
        scored_csv = run_score(enriched_csv, scoring_config)
        run_emails(scored_csv, email_config)


if __name__ == "__main__":
    main()
