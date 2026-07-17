# Recruitment Data Cleaning Agent

A public, privacy-safe portfolio version of a recruitment CSV cleaning agent. The original work solved messy crawler exports, inconsistent schemas, invalid job links, duplicate postings, and weak auditability. This repository keeps the reusable engineering pattern while replacing all private data with synthetic sample data.

## Background

Recruitment datasets collected from web tools often arrive as many CSV files with mixed encodings, crawler column names, duplicated postings, malformed links, and inconsistent city or company fields. The operational requirement was to turn those files into a repeatable, auditable delivery workflow instead of manual notebook cleanup.

## Original Problems

- Raw exports used unstable column names such as `sal`, `er`, `er1`, `er2`, and `字段1`.
- Job links could contain tracking parameters, invisible characters, or invalid hosts.
- The same job could appear multiple times across collection batches.
- Manual notebook runs were hard to test, reproduce, or review.
- Reports were needed to explain row drops, duplicate handling, and output quality.

## My Solution

I converted the workflow into an Agent-oriented project with a documented skill, command-line scripts, tests, sample data, demo outputs, and a publication safety validator. The public version demonstrates the same core ideas with synthetic data only.

## Agent Workflow

1. Read the recruitment-data-cleaning skill instructions.
2. Load synthetic raw CSV data from `sample_data/raw/`.
3. Normalize schema and job URLs.
4. Drop invalid job links.
5. Deduplicate by stable job ID, keeping the latest record by default.
6. Export a clean CSV and machine-readable quality report.
7. Run tests and validate that the repository is safe to publish.

## Tech Stack

- Python 3.10+
- Standard-library CSV processing for portability
- `unittest` for test coverage
- YAML Agent config
- Markdown reports

## Test Results

Current validation artifacts are in `demo_outputs/` and `portfolio_validation_report.md`.

Expected local checks:

```bash
python -m unittest discover -s tests
python scripts/validate_portfolio.py --root . --output portfolio_validation_report.md
```

## Run

```bash
python scripts/generate_sample_data.py --output sample_data/raw/sample_recruitment_raw.csv --rows 104
python scripts/clean_recruitment_data.py   --input sample_data/raw/sample_recruitment_raw.csv   --output demo_outputs/cleaned_sample.csv   --quality-report demo_outputs/quality_report.json   --validation-report demo_outputs/validation_report.md   --overwrite
python -m unittest discover -s tests
python scripts/validate_portfolio.py --root . --output portfolio_validation_report.md
```

## Privacy

This repository intentionally excludes real recruitment data, internal notebooks, cookies, tokens, account information, historical aggregates, private operator paths, and large source archives.
