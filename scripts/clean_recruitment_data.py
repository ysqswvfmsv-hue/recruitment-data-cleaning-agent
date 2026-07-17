#!/usr/bin/env python3
"""Clean synthetic recruitment CSV exports for the public portfolio demo."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

FINAL_COLUMNS = ["城市", "标题", "标题链接", "薪资", "公司名称", "公司性质", "公司规模", "行业领域", "采集时的时间"]
RENAME_MAP = {"sal": "薪资", "er": "公司名称", "er1": "公司性质", "er2": "行业领域", "字段1": "公司规模"}
JOB_URL_RE = re.compile(r"^https://(?:jobs\.example\.com|jobs\.51job\.example)/([^/?#]+)/([0-9]+)\.html(?:[?#].*)?$", re.I)
INVISIBLE_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff\xa0]")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_time(value: str) -> datetime:
    text = (value or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return datetime.min


def normalize_url(value: str) -> str:
    text = INVISIBLE_RE.sub("", value or "").strip()
    match = JOB_URL_RE.match(text)
    if not match:
        return text
    city, job_id = match.groups()
    host = text.split("/", 3)[2].lower()
    return f"https://{host}/{city.lower()}/{job_id}.html"


def extract_job_id(url: str) -> str:
    match = JOB_URL_RE.match(url or "")
    return match.group(2) if match else ""


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    merged = {RENAME_MAP.get(k, k): (v or "").strip() for k, v in row.items()}
    out = {col: merged.get(col, "") for col in FINAL_COLUMNS}
    out["标题链接"] = normalize_url(out["标题链接"])
    return out


def choose_duplicate(existing: dict[str, str], candidate: dict[str, str], mode: str) -> dict[str, str]:
    if mode == "first":
        return existing
    if mode == "last":
        return candidate
    return candidate if parse_time(candidate.get("采集时的时间", "")) >= parse_time(existing.get("采集时的时间", "")) else existing


def clean_rows(rows: Iterable[dict[str, str]], dedup_keep: str = "latest") -> tuple[list[dict[str, str]], dict[str, object]]:
    stats = Counter()
    by_id: dict[str, dict[str, str]] = {}
    duplicate_ids = Counter()

    for raw in rows:
        stats["input_rows"] += 1
        row = normalize_row(raw)
        job_id = extract_job_id(row["标题链接"])
        if not job_id:
            stats["invalid_job_links"] += 1
            continue
        if job_id in by_id:
            stats["duplicate_rows"] += 1
            duplicate_ids[job_id] += 1
            by_id[job_id] = choose_duplicate(by_id[job_id], row, dedup_keep)
        else:
            by_id[job_id] = row

    cleaned = sorted(by_id.values(), key=lambda r: (r.get("城市", ""), extract_job_id(r.get("标题链接", ""))))
    stats["output_rows"] = len(cleaned)
    stats["unique_job_ids"] = len(by_id)
    stats["city_non_empty"] = sum(1 for r in cleaned if r.get("城市"))
    stats["salary_non_empty"] = sum(1 for r in cleaned if r.get("薪资"))
    report = dict(stats)
    report["duplicate_job_ids"] = sorted(duplicate_ids)
    report["columns"] = FINAL_COLUMNS
    return cleaned, report


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FINAL_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_validation(path: Path, quality: dict[str, object], input_path: Path, output_path: Path) -> None:
    status = "PASS" if quality.get("invalid_job_links", 0) >= 0 and quality.get("output_rows", 0) > 0 else "FAIL"
    text = f"""# Validation Report

- Status: {status}
- Input file: `{input_path.as_posix()}`
- Output file: `{output_path.as_posix()}`
- Input rows: {quality.get('input_rows')}
- Output rows: {quality.get('output_rows')}
- Invalid links dropped: {quality.get('invalid_job_links')}
- Duplicate rows removed: {quality.get('duplicate_rows')}
- Unique job IDs: {quality.get('unique_job_ids')}
- Non-empty city rows: {quality.get('city_non_empty')}
- Non-empty salary rows: {quality.get('salary_non_empty')}
"""
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean synthetic recruitment CSV data.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--quality-report", default="demo_outputs/quality_report.json")
    parser.add_argument("--validation-report", default="demo_outputs/validation_report.md")
    parser.add_argument("--dedup-keep", choices=["first", "last", "latest"], default="latest")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if output_path.exists() and not args.overwrite:
        raise SystemExit(f"Output exists: {output_path}. Use --overwrite to replace it.")

    rows = read_rows(input_path)
    cleaned, quality = clean_rows(rows, args.dedup_keep)
    quality["input_sha256"] = sha256_file(input_path)
    quality["generated_at"] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    write_csv(output_path, cleaned)
    Path(args.quality_report).write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    write_validation(Path(args.validation_report), quality, input_path, output_path)
    print(json.dumps({"status": "ok", "output_rows": len(cleaned), "quality_report": args.quality_report}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
