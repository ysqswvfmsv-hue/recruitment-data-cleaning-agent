import csv
import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from clean_recruitment_data import clean_rows, extract_job_id, normalize_url, FINAL_COLUMNS


class CleanerTests(unittest.TestCase):
    def test_normalize_url_removes_tracking_query(self):
        self.assertEqual(
            normalize_url(" https://JOBS.EXAMPLE.COM/Shanghai/123.html?from=x "),
            "https://jobs.example.com/shanghai/123.html",
        )

    def test_extract_job_id(self):
        self.assertEqual(extract_job_id("https://jobs.example.com/beijing/900001.html"), "900001")
        self.assertEqual(extract_job_id("https://example.invalid/jobs/900001"), "")

    def test_clean_rows_maps_fields_drops_invalid_and_deduplicates_latest(self):
        rows = [
            {"城市": "上海", "标题": "旧", "标题链接": "https://jobs.example.com/shanghai/1.html", "sal": "8-10K", "er": "A", "er1": "民营", "字段1": "50-150人", "er2": "互联网", "采集时的时间": "2026-01-01 10:00:00"},
            {"城市": "上海", "标题": "新", "标题链接": "https://jobs.example.com/shanghai/1.html", "sal": "9-12K", "er": "A", "er1": "民营", "字段1": "50-150人", "er2": "互联网", "采集时的时间": "2026-01-02 10:00:00"},
            {"城市": "北京", "标题": "坏链接", "标题链接": "https://bad.example/1", "sal": "9-12K", "er": "B", "er1": "外企", "字段1": "500人", "er2": "服务", "采集时的时间": "2026-01-02 10:00:00"},
        ]
        cleaned, report = clean_rows(rows)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["标题"], "新")
        self.assertEqual(cleaned[0]["薪资"], "9-12K")
        self.assertEqual(report["input_rows"], 3)
        self.assertEqual(report["invalid_job_links"], 1)
        self.assertEqual(report["duplicate_rows"], 1)

    def test_final_columns_are_stable(self):
        self.assertEqual(FINAL_COLUMNS, ["城市", "标题", "标题链接", "薪资", "公司名称", "公司性质", "公司规模", "行业领域", "采集时的时间"])


if __name__ == "__main__":
    unittest.main()
