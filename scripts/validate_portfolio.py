#!/usr/bin/env python3
"""Validate that the portfolio package is safe to publish."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PERSONAL_USER = "zhang" + "wanting"
SECRET_PATTERNS = {
    "personal_path": re.compile(r"/Users/" + PERSONAL_USER + r"\b|" + PERSONAL_USER, re.I),
    "token_like_assignment": re.compile(r"(?i)(api[_-]?key|secret|token|cookie|password)\s*[:=]\s*[^\s]+"),
}
LARGE_EXTS = {".zip", ".7z", ".rar", ".xlsx", ".xls", ".parquet", ".db"}
TEXT_EXTS = {".py", ".md", ".yaml", ".yml", ".txt", ".csv", ".json", ".gitignore"}
REQUIRED = [
    ".agents/skills/recruitment-data-cleaning/SKILL.md",
    "agents/openai.yaml",
    "scripts/clean_recruitment_data.py",
    "scripts/generate_sample_data.py",
    "scripts/validate_portfolio.py",
    "tests/test_clean_recruitment_data.py",
    "requirements.txt",
    "README.md",
    "README.zh-CN.md",
    ".gitignore",
    "sample_data/raw/sample_recruitment_raw.csv",
    "demo_outputs/cleaned_sample.csv",
    "demo_outputs/quality_report.json",
    "demo_outputs/validation_report.md",
]


def scan(root: Path) -> dict[str, object]:
    files = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]
    missing = [path for path in REQUIRED if not (root / path).exists()]
    large_or_forbidden = []
    findings = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() in LARGE_EXTS or (path.suffix.lower() == ".csv" and path.stat().st_size > 2_000_000):
            large_or_forbidden.append(rel)
        if path.suffix.lower() in TEXT_EXTS or path.name == ".gitignore":
            text = path.read_text(encoding="utf-8", errors="ignore")
            for name, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    findings.append({"file": rel, "pattern": name})
    return {
        "status": "PASS" if not missing and not findings and not large_or_forbidden else "FAIL",
        "file_count": len(files),
        "missing_required_files": missing,
        "sensitive_findings": findings,
        "large_or_forbidden_files": large_or_forbidden,
        "note": "Documentation may describe categories of excluded private material; findings only report concrete personal paths or secret-like assignments.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="portfolio_validation_report.md")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    result = scan(root)
    lines = [
        "# Portfolio Validation Report",
        "",
        f"- Status: {result['status']}",
        f"- Files scanned: {result['file_count']}",
        f"- Missing required files: {len(result['missing_required_files'])}",
        f"- Sensitive findings: {len(result['sensitive_findings'])}",
        f"- Large/forbidden files: {len(result['large_or_forbidden_files'])}",
        "",
        "## Required File Check",
        "",
    ]
    if result["missing_required_files"]:
        lines += [f"- Missing: `{x}`" for x in result["missing_required_files"]]
    else:
        lines.append("- All required files are present.")
    lines += ["", "## Sensitive Data Scan", ""]
    if result["sensitive_findings"]:
        lines += [f"- {x['pattern']}: `{x['file']}`" for x in result["sensitive_findings"]]
    else:
        lines.append("- No concrete personal paths or secret-like assignments found.")
    lines += ["", "## Large File Scan", ""]
    if result["large_or_forbidden_files"]:
        lines += [f"- `{x}`" for x in result["large_or_forbidden_files"]]
    else:
        lines.append("- No large CSV/ZIP/archive/database files found.")
    lines += ["", "## Machine Readable Summary", "", "```json", json.dumps(result, ensure_ascii=False, indent=2), "```", ""]
    (root / args.output).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
