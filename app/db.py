import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]


def connect():
    return psycopg.connect(
        os.getenv("DATABASE_URL", "postgresql://dataflow:dataflow@localhost:5432/dataflow"),
        row_factory=dict_row,
        connect_timeout=5,
    )


def migrate():
    with connect() as db:
        db.execute("SELECT pg_advisory_xact_lock(423809)")
        for migration in sorted((ROOT / "sql").glob("*.sql")):
            db.execute(migration.read_text(), prepare=False)
