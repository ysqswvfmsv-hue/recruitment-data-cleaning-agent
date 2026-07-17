---
name: recruitment-data-cleaning
description: Clean, merge, audit, and validate recruitment CSV exports for public demo datasets. Use when Codex needs to normalize job links, map raw crawler columns, remove invalid records, deduplicate by job ID, generate quality reports, or validate that outputs are safe to publish.
---

# Recruitment Data Cleaning Skill

This public portfolio skill demonstrates a privacy-safe recruitment CSV cleaning workflow. It is intentionally dataset-agnostic and ships only with synthetic sample data.

## When to Use

Use this skill when a task involves:

- Cleaning raw recruitment CSV exports.
- Normalizing job detail URLs and extracting stable job IDs.
- Mapping crawler columns such as `sal`, `er`, `er1`, `er2`, and `字段1` to business fields.
- Dropping invalid job links.
- Deduplicating records by job ID.
- Producing quality and validation reports.

## Public Workflow

1. Treat `sample_data/raw/` as read-only demo input.
2. Run the cleaner:

```bash
python scripts/clean_recruitment_data.py   --input sample_data/raw/sample_recruitment_raw.csv   --output demo_outputs/cleaned_sample.csv   --quality-report demo_outputs/quality_report.json   --validation-report demo_outputs/validation_report.md   --dedup-keep latest   --overwrite
```

3. Run tests:

```bash
python -m unittest discover -s tests
```

4. Validate the public portfolio package:

```bash
python scripts/validate_portfolio.py --root . --output portfolio_validation_report.md
```

## Cleaning Rules

- Keep only valid recruitment detail links matching `https://jobs.example.com/<city>/<numeric_id>.html` or `https://jobs.51job.example/<city>/<numeric_id>.html` in this public demo.
- Normalize URL host and path case where safe, strip tracking query strings, and preserve the numeric job ID.
- Deduplicate by extracted job ID, keeping the latest record by `采集时的时间` by default.
- Map raw crawler fields to normalized business fields:
  - `sal` -> `薪资`
  - `er` -> `公司名称`
  - `er1` -> `公司性质`
  - `er2` -> `行业领域`
  - `字段1` -> `公司规模`
- Do not infer city from company name, file name, operator name, personal paths, or private task names.
- Produce audit fields in reports, not in the final delivery CSV.

## Safety Rules

- Never include real raw recruitment exports, historical aggregate files, notebooks, cookies, tokens, account IDs, or private team metadata in a public package.
- Scan the project before publishing for personal paths, secrets, large CSV/ZIP files, and internal directory names.
- Use synthetic data for demos and tests.
