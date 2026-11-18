"""Exercise the running server and optionally capture generated reports."""
import csv
from io import BytesIO
import json
from pathlib import Path
from statistics import median, quantiles
import sys
from time import perf_counter
from urllib.request import urlopen

from openpyxl import load_workbook

BASE = "http://127.0.0.1:8000"
DEST = Path(sys.argv[1]) if len(sys.argv)>1 else None


def fetch(path):
    with urlopen(BASE + path, timeout=25) as response:
        return response.read()


def api(path):
    return json.loads(fetch("/api/v1/" + path))


def main():
    assert b"ok" in fetch("/health")
    assert b"DataFlow Intelligence" in fetch("/")
    assert b"/api/v1/dashboard/summary" in fetch("/openapi.json")
    paths = ("dashboard/summary", "revenue/trends", "customers/segments", "customers/cohorts",
             "marketing/funnel", "marketing/campaigns", "products/performance", "experiments",
             "quality", "pipelines/runs")
    data = {path:api(path) for path in paths}
    assert all(data.values())
    assert data["dashboard/summary"][0]["orders"] >= 2500
    assert int(data["dashboard/summary"][0]["net_revenue"]) == sum(int(r["net_revenue"]) for r in data["revenue/trends"])
    assert all(row["failures"] == 0 for row in data["quality"])
    assert all(float(row["retention_pct"]) == 100 for row in data["customers/cohorts"] if row["cohort"]==row["activity_month"])
    book_bytes = fetch("/api/v1/reports/export")
    book = load_workbook(BytesIO(book_bytes), data_only=True)
    columns = [c.value for c in book["Summary"][1]]
    revenue = book["Summary"][2][columns.index("net_revenue")].value
    assert round(revenue*100) == int(data["dashboard/summary"][0]["net_revenue"])
    if DEST:
        DEST.mkdir(parents=True, exist_ok=True)
        (DEST/"NovaCart_Business_Analysis.xlsx").write_bytes(book_bytes)
    for name in ("Summary","Revenue","Cohorts","Segments","Funnel","Campaigns","Products","Quality"):
        payload = fetch(f"/api/v1/reports/export?format=csv&report={name}")
        assert list(csv.DictReader(payload.decode().splitlines()))
        if DEST:
            (DEST/f"{name}.csv").write_bytes(payload)
    samples = []
    for _ in range(30):
        begin = perf_counter()
        api("dashboard/summary")
        samples.append((perf_counter()-begin)*1000)
    print(f"PASS: health, dashboard, OpenAPI, {len(paths)} analytics routes, reconciliation, data quality, workbook and 8 CSV exports")
    print(f"Summary HTTP latency, 30 sequential requests: p50 {median(samples):.1f} ms, p95 {quantiles(samples,n=100)[94]:.1f} ms")


if __name__ == "__main__":
    main()
