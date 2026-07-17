#!/usr/bin/env python3
"""Generate synthetic recruitment rows for the public demo."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta
from pathlib import Path

CITIES = ["上海", "北京", "深圳", "杭州", "成都", "南京", "武汉", "苏州", "广州", "天津"]
SLUGS = ["shanghai", "beijing", "shenzhen", "hangzhou", "chengdu", "nanjing", "wuhan", "suzhou", "guangzhou", "tianjin"]
ROLES = ["数据分析师", "招聘运营专员", "Python工程师", "数据清洗工程师", "BI分析师", "爬虫工程师", "HR数据顾问"]
INDUSTRIES = ["互联网", "企业服务", "智能制造", "金融科技", "教育科技"]
SIZES = ["50-150人", "150-500人", "500-1000人", "1000人以上"]
TYPES = ["民营", "合资", "上市公司", "外企"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="sample_data/raw/sample_recruitment_raw.csv")
    parser.add_argument("--rows", type=int, default=104)
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["城市", "标题", "标题链接", "sal", "er", "er1", "字段1", "er2", "采集时的时间"]
    start = datetime(2026, 6, 1, 9, 0, 0)
    rows = []
    for i in range(args.rows):
        city_idx = i % len(CITIES)
        job_id = 900000 + i
        if i in (25, 50, 75):
            job_id -= 1
        url = f"https://jobs.example.com/{SLUGS[city_idx]}/{job_id}.html?from=demo" if i % 9 == 0 else f"https://jobs.example.com/{SLUGS[city_idx]}/{job_id}.html"
        if i in (17, 88):
            url = f"https://example.invalid/jobs/{job_id}"
        rows.append({
            "城市": CITIES[city_idx],
            "标题": f"{ROLES[i % len(ROLES)]}-{i:03d}",
            "标题链接": url,
            "sal": f"{8 + (i % 8)}-{14 + (i % 10)}K",
            "er": f"示例科技{i % 18:02d}有限公司",
            "er1": TYPES[i % len(TYPES)],
            "字段1": SIZES[i % len(SIZES)],
            "er2": INDUSTRIES[i % len(INDUSTRIES)],
            "采集时的时间": (start + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S"),
        })

    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
