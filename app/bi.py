"""Export a transactionally consistent analytics model and validate its grains."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from app.db import connect
from app.reports import SHEETS, export_rows
from app.statistics import checkout_experiment

QUERIES = {
    "DimDate": """
        SELECT d::date AS date_key, extract(year from d)::integer AS year,
          extract(month from d)::integer AS month_number, to_char(d,'YYYY-MM') AS year_month
        FROM generate_series((SELECT min(signup) FROM customers)::timestamp,
          (SELECT greatest(max(ordered),(SELECT max(visited) FROM sessions)) FROM orders)::timestamp,
          '1 day') d ORDER BY d
    """,
    "DimCustomer": "SELECT id AS customer_id,signup,region,channel,segment FROM customers ORDER BY id",
    "DimProduct": "SELECT id AS product_id,name,category,price,cost,stock FROM products ORDER BY id",
    "DimCampaign": "SELECT id AS campaign_id,channel,spend,impressions,clicks FROM campaigns ORDER BY id",
    "FactOrder": """
        SELECT f.id AS order_id,f.customer_id,f.ordered AS date_key,f.campaign_id,
          f.gross AS gross_cents,f.sales AS sales_cents,f.refund AS refund_cents,
          f.sales-f.refund AS net_cents,f.cost AS cost_cents,
          f.sales-f.refund-f.cost AS profit_cents,o.payment
        FROM order_facts f JOIN orders o ON o.id=f.id ORDER BY f.id
    """,
    "FactOrderLine": """
        SELECT i.order_id,i.product_id,o.ordered AS date_key,o.customer_id,
          i.quantity,i.quantity::bigint*(i.unit_price-i.discount) AS sales_cents,
          i.quantity::bigint*i.unit_cost AS cost_cents
        FROM items i JOIN orders o ON o.id=i.order_id ORDER BY i.order_id,i.product_id
    """,
    "FactSession": """
        SELECT id AS session_id,customer_id,visited AS date_key,variant,device,
          cart::integer AS carts,converted::integer AS conversions FROM sessions ORDER BY id
    """,
}

INTEGER_FIELDS = set("""
    year month_number customer_id product_id campaign_id price cost stock spend impressions clicks
    order_id gross_cents sales_cents refund_cents net_cents cost_cents profit_cents quantity
    session_id carts conversions
""".split())

RELATIONSHIPS = (
    ("FactOrder","customer_id","DimCustomer"),
    ("FactOrder","date_key","DimDate"),
    ("FactOrder","campaign_id","DimCampaign"),
    ("FactOrderLine","order_id","FactOrder"),
    ("FactOrderLine","product_id","DimProduct"),
    ("FactOrderLine","date_key","DimDate"),
    ("FactOrderLine","customer_id","DimCustomer"),
    ("FactSession","date_key","DimDate"),
    ("FactSession","customer_id","DimCustomer"),
)
PRIMARY_KEYS = {
    "DimDate": ("date_key",), "DimCustomer": ("customer_id",), "DimProduct": ("product_id",),
    "DimCampaign": ("campaign_id",), "FactOrder": ("order_id",),
    "FactOrderLine": ("order_id", "product_id"), "FactSession": ("session_id",),
}


def write_csv(directory, name, columns, rows):
    with (directory / f"{name}.csv").open("w",encoding="utf-8",newline="") as output:
        writer = csv.DictWriter(output,columns)
        writer.writeheader()
        writer.writerows(rows)


def load_tables(directory, db):
    """Load published CSVs into SQLite for independent SQL validation."""
    db.execute("PRAGMA foreign_keys = ON")
    for name in QUERIES:
        with (directory / f"{name}.csv").open(encoding="utf-8",newline="") as source:
            reader = csv.DictReader(source)
            columns = reader.fieldnames
            declarations = [f'"{column}" {"INTEGER" if column in INTEGER_FIELDS else "TEXT"}'
                            for column in columns]
            key = PRIMARY_KEYS[name]
            declarations = [f"{declaration} NOT NULL" if column in key else declaration
                            for column,declaration in zip(columns,declarations)]
            declarations.append("PRIMARY KEY (" + ",".join(key) + ")")
            declarations.extend(f"FOREIGN KEY ({column}) REFERENCES {target} ({column})"
                                for table,column,target in RELATIONSHIPS if table == name)
            db.execute(f'CREATE TABLE "{name}" ({",".join(declarations)})')
            marks = ",".join("?" for _ in columns)
            db.executemany(f'INSERT INTO "{name}" VALUES ({marks})',
                           (tuple(row[column] if row[column] != "" else None for column in columns)
                            for row in reader))


def reconcile(directory, expected):
    with sqlite3.connect(":memory:") as db:
        load_tables(directory,db)
        totals = db.execute("""
          SELECT count(*),sum(net_cents),sum(profit_cents),sum(sales_cents),
            sum(refund_cents),count(DISTINCT customer_id) FROM FactOrder
        """).fetchone()
        if tuple(expected[k] for k in ("orders","net_cents","profit_cents","sales_cents",
                                       "refund_cents","active_customers")) != totals:
            raise ValueError("The BI model does not reconcile to PostgreSQL")
        unmatched = db.execute("""
          SELECT count(*) FROM FactOrder o LEFT JOIN (
            SELECT order_id, sum(sales_cents) AS sales, sum(cost_cents) AS cost
            FROM FactOrderLine GROUP BY order_id
          ) l ON l.order_id=o.order_id WHERE l.order_id IS NULL OR l.sales<>o.sales_cents
             OR l.cost<>o.cost_cents OR o.sales_cents-o.refund_cents<>o.net_cents
             OR o.net_cents-o.cost_cents<>o.profit_cents
        """).fetchone()[0]
        if unmatched:
            raise ValueError(f"Line and order totals differ for {unmatched} orders")
        sessions, conversions, bad_sessions = db.execute("""
          SELECT count(*),sum(conversions),sum(CASE WHEN conversions>carts THEN 1 ELSE 0 END)
          FROM FactSession
        """).fetchone()
        if bad_sessions:
            raise ValueError("Session conversions exceed cart events")
        return {"sessions":sessions, "conversions":conversions}


def export(destination):
    destination = destination.resolve()
    destination.mkdir(parents=True,exist_ok=True)
    with TemporaryDirectory(dir=destination) as staging:
        folder = Path(staging)
        with connect() as db:
            db.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
            start,end = db.execute("SELECT min(ordered),max(ordered) FROM orders").fetchone().values()
            if start is None:
                raise RuntimeError("Start DataFlow to create the base dataset before exporting")
            bounds = db.execute("""
                SELECT least(%s,min(visited)) AS start,greatest(%s,max(visited)) AS end FROM sessions
            """,(start,end)).fetchone()
            for name,query in QUERIES.items():
                rows = db.execute(query)
                write_csv(folder,name,[c.name for c in rows.description],rows)
            for name,key in SHEETS.items():
                columns,rows = export_rows(db,key,bounds)
                write_csv(folder,name,columns,rows)
            result = db.execute("""
              SELECT count(*) AS orders,sum(sales-refund) AS net_cents,
               sum(sales-refund-cost) AS profit_cents,sum(sales) AS sales_cents,
               sum(refund) AS refund_cents,count(DISTINCT customer_id) AS active_customers
              FROM order_facts
            """).fetchone()
            totals = {k:int(v) for k,v in result.items()}
            variants = db.execute("""
              SELECT variant,count(*) AS n,count(*) FILTER(WHERE converted) AS successes
              FROM sessions GROUP BY variant ORDER BY variant
            """).fetchall()
            write_csv(folder,"ExperimentArms",["variant","n","successes"],variants)
            experiment = checkout_experiment({r["variant"]:(r["n"],r["successes"]) for r in variants})
            write_csv(folder,"Experiment",list(experiment),[experiment])
        totals.update(reconcile(folder,totals))
        hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.glob("*.csv"))}
        manifest = {"start":str(bounds["start"]),"end":str(bounds["end"]),
                    "currency":"USD cents","synthetic":True,"totals":totals,"sha256":hashes}
        (folder/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
        for name in [*hashes,"manifest.json"]:
            (folder/name).replace(destination/name)
    return manifest


def check(directory):
    manifest = json.loads((directory/"manifest.json").read_text(encoding="utf-8"))
    for name,digest in manifest["sha256"].items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Snapshot checksum differs for {name}")
    if any(manifest["totals"][key] != value
           for key,value in reconcile(directory,manifest["totals"]).items()):
        raise ValueError("Session totals differ from snapshot manifest")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=["export","check"])
    parser.add_argument("directory",type=Path)
    args = parser.parse_args()
    result = export(args.directory) if args.action == "export" else check(args.directory)
    print(json.dumps(result["totals"],indent=2))


if __name__ == "__main__":
    main()
