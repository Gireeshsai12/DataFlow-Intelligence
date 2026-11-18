"""Run portable analytics exercises and generate a short business case study."""
import argparse
import csv
from decimal import Decimal
from pathlib import Path
import sqlite3

from app.bi import INTEGER_FIELDS, check, load_tables, write_csv
from app.db import ROOT, connect


def results(db, query):
    cursor = db.execute(query)
    headers = [column[0] for column in cursor.description]
    return headers, [dict(zip(headers,row)) for row in cursor.fetchall()]


def usd(cents):
    return f"${Decimal(cents)/100:,.2f}"


def brief(path, manifest, calculated):
    totals = manifest["totals"]
    months = calculated["monthly_revenue"]
    peak = max(months,key=lambda row:row["net_cents"])
    dec = months[-1]
    regions = calculated["region_revenue"]
    top = regions[0]
    with (path/"Experiment.csv").open(encoding="utf-8",newline="") as data:
        experiment = next(csv.DictReader(data))
    case = f"""# NovaCart business review

Synthetic portfolio case study · {manifest['start']} through {manifest['end']}

## Executive brief

NovaCart booked **{usd(totals['net_cents'])}** in net revenue on **{totals['orders']:,} orders**.
Gross profit was **{usd(totals['profit_cents'])}**. Revenue subtracts refunds from post-discount
sales. Experiment conversions come from the independent session dataset.

## Sales

The highest net-revenue month was {peak['year_month']} at {usd(peak['net_cents'])}.
The final month, {dec['year_month']}, ended at {usd(dec['net_cents'])}.
Compare orders and AOV by week and check the data cutoff before attributing that change to demand.

## Regional performance

{top['region']} led with {usd(top['net_cents'])} from {top['orders']} orders.
Compare revenue per active customer and acquisition mix before shifting campaign spend.

## Checkout experiment

Treatment converted {float(experiment['treatment_rate_pct']):.2f}% of sessions versus
{float(experiment['control_rate_pct']):.2f}% for control. The estimated difference was
{float(experiment['effect_pp']):.2f} percentage points, with an approximate 95% interval
from {float(experiment['ci_low_pp']):.2f} to {float(experiment['ci_high_pp']):.2f}
percentage points. The two-sided p-value was {float(experiment['p_value']):.4f}.
{experiment['recommendation']} Before a rollout decision, define a minimum practical
lift and add refund and order-value guardrails.

## Decision review

Review the three findings with the scenario owner. Confirm completeness, assign an owner
to investigate month-end coverage, and agree on success and rollback criteria for the
checkout experiment. See bi/case-study/Acceptance.md for requirements and UAT steps.
"""
    (path/"BusinessReview.md").write_text(case,encoding="utf-8")


def run(path, write=False, postgres=False):
    manifest = check(path)
    calculated = {}
    with sqlite3.connect(":memory:") as db:
        load_tables(path,db)
        for sql in sorted((ROOT/"bi"/"sql").glob("*.sql")):
            headers, rows = results(db,sql.read_text())
            calculated[sql.stem] = rows
            if write:
                folder = path/"expected"
                folder.mkdir(exist_ok=True)
                write_csv(folder,sql.stem,headers,rows)
            elif (path/"expected"/f"{sql.stem}.csv").exists():
                with (path/"expected"/f"{sql.stem}.csv").open(encoding="utf-8",newline="") as expected:
                    assert list(csv.DictReader(expected)) == [
                        {key: "" if val is None else str(val) for key,val in row.items()} for row in rows
                    ], sql.name
    totals = manifest["totals"]
    for name in ("monthly_revenue","region_revenue"):
        assert sum(row["net_cents"] for row in calculated[name]) == totals["net_cents"]
        assert sum(row["orders"] for row in calculated[name]) == totals["orders"]
    assert sum(row["conversions"] for row in calculated["checkout"]) == totals["conversions"]
    if postgres:
        with connect() as db:
            for table in ("DimDate","DimCustomer","DimProduct","FactOrder","FactOrderLine","FactSession"):
                with (path/f"{table}.csv").open(encoding="utf-8",newline="") as source:
                    reader = csv.DictReader(source)
                    columns = ", ".join(f"{c} {'bigint' if c in INTEGER_FIELDS else 'text'}"
                                        for c in reader.fieldnames)
                    db.execute(f"CREATE TEMP TABLE {table} ({columns})")
                    with db.cursor().copy(f"COPY {table} FROM STDIN") as writer:
                        for row in reader:
                            writer.write_row([val or None for val in row.values()])
            for sql in sorted((ROOT/"bi"/"sql").glob("*.sql")):
                assert db.execute(sql.read_text()).fetchall() == calculated[sql.stem], sql.name
    if write:
        brief(path,manifest,calculated)
    print(f"PASS: snapshot checksums, model reconciliation, {len(calculated)} analytical queries"
          + (" matched across SQLite and PostgreSQL" if postgres else ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot",type=Path)
    parser.add_argument("--write",action="store_true")
    parser.add_argument("--postgres",action="store_true")
    args = parser.parse_args()
    run(args.snapshot,args.write,args.postgres)
