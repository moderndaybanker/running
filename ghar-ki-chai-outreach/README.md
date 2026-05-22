# Ghar Ki Chai Outreach

A local Python workflow for finding, enriching, scoring, and drafting personalised outreach to potential stockists and collaborators for **Ghar Ki Chai**, a UK-based premium instant chai brand.

The project is designed to be repeatable and safe for review-led outreach:

- It can generate search queries for target categories and locations.
- It can search the web through a pluggable provider.
- It saves raw, enriched, scored, and final CSV files.
- It visits prospect websites to look for emails, Instagram links, contact pages, and useful notes.
- It deduplicates leads by website.
- It scores each lead for fit with Ghar Ki Chai.
- It creates personalised email and follow-up drafts for human review.
- **It does not send emails automatically.**

## Target prospects

The starter configuration focuses on:

- Independent delis
- Premium cafés
- Farm shops
- Gift shops
- Wellness stores
- Yoga studios
- Boutique hotels
- South Asian food stores
- Corporate gifting buyers
- Concept stores
- Premium grocers

## Target geography

The first search configuration focuses on London and the South East of England, including London, Brighton, Oxford, Cambridge, Guildford, Reading, Sevenoaks, Tunbridge Wells, Canterbury, and Windsor.

## Project structure

```text
ghar-ki-chai-outreach/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   ├── search_config.yaml
│   ├── scoring_config.yaml
│   └── email_templates.yaml
├── data/
│   ├── raw/
│   ├── enriched/
│   └── final/
├── outputs/
│   ├── emails/
│   └── reports/
└── src/
    ├── main.py
    ├── lead_researcher.py
    ├── lead_enricher.py
    ├── lead_scorer.py
    ├── email_generator.py
    ├── utils.py
    └── config_loader.py
```

## Quick start for non-engineers

### 1. Open a terminal in this folder

```bash
cd ghar-ki-chai-outreach
```

### 2. Create a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install requirements

```bash
pip install -r requirements.txt
```

### 4. Create your environment file

Copy the example environment file:

```bash
cp .env.example .env
```

Then open `.env` and choose a search provider.

The safest first run is:

```text
SEARCH_PROVIDER=mock
```

This creates example rows without using a paid search API.

For live web search, set one of:

```text
SEARCH_PROVIDER=serpapi
SERPAPI_API_KEY=your_serpapi_key_here
```

or:

```text
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your_tavily_key_here
```

## Running the workflow

### Run everything

```bash
python src/main.py run-all
```

This will:

1. Generate search queries from `config/search_config.yaml`.
2. Search using the configured provider.
3. Save raw leads to `data/raw/`.
4. Enrich websites and deduplicate leads.
5. Save enriched leads to `data/enriched/`.
6. Score leads and save a scored CSV to `data/final/`.
7. Generate draft email text files in `outputs/emails/`.
8. Save a final outreach CSV in `data/final/`.

### Run one step at a time

Research only:

```bash
python src/main.py research
```

Enrich a raw CSV:

```bash
python src/main.py enrich --raw-csv data/raw/raw_leads_YYYYMMDD_HHMMSS.csv
```

Score an enriched CSV:

```bash
python src/main.py score --enriched-csv data/enriched/enriched_leads_YYYYMMDD_HHMMSS.csv
```

Generate email drafts from a scored CSV:

```bash
python src/main.py emails --scored-csv data/final/scored_leads_YYYYMMDD_HHMMSS.csv
```

## Configuration files

### `config/search_config.yaml`

Change categories, locations, query templates, the search provider, results per query, maximum queries, and rate limiting.

### `config/scoring_config.yaml`

Adjust lead scoring weights. A lead can earn points for category fit, relevant keywords, contact information, website availability, Instagram presence, and target geography.

### `config/email_templates.yaml`

Edit the initial outreach and follow-up templates. The generator fills in fields such as business name, category, location, and personalisation points.

## Safety and compliance notes

- This project creates draft outreach only. It never sends emails.
- Use the output CSV and email drafts for manual review before contacting anyone.
- Respect website terms, privacy rules, and relevant UK data protection and marketing laws.
- Rate limiting is enabled through `RATE_LIMIT_SECONDS` in `.env` and `search.rate_limit_seconds` in `config/search_config.yaml`.
- Keep API keys in `.env`. Do not commit real API keys to version control.

## Outputs

Typical files created during a run:

- `data/raw/raw_leads_YYYYMMDD_HHMMSS.csv`
- `data/enriched/enriched_leads_YYYYMMDD_HHMMSS.csv`
- `data/final/scored_leads_YYYYMMDD_HHMMSS.csv`
- `data/final/final_outreach_YYYYMMDD_HHMMSS.csv`
- `outputs/emails/001_Example_Business.txt`

## Troubleshooting

### The search results are fake examples

Check `.env`. If `SEARCH_PROVIDER=mock`, the project intentionally uses mock data. Set `SEARCH_PROVIDER=serpapi` or `SEARCH_PROVIDER=tavily` and add the matching API key for live search.

### A website cannot be enriched

Some sites block bots, load content with JavaScript, or time out. The workflow logs the error and continues so one failed site does not stop the whole run.

### The score does not look right

Edit `config/scoring_config.yaml`. The scoring model is intentionally simple so it can be reviewed and adjusted without changing Python code.
