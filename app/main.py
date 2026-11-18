from contextlib import asynccontextmanager
from datetime import date
import os
from pathlib import Path
import secrets
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.db import connect, migrate, ROOT
from app.metrics import QUERIES
from app.pipeline import refresh
from app.reports import SHEETS, csv_data, export_rows, workbook
from app.statistics import checkout_experiment, sample_size


@asynccontextmanager
async def lifespan(_app):
    migrate()
    refresh(only_if_empty=True)
    yield


app = FastAPI(title="DataFlow Intelligence", version="1.0", lifespan=lifespan)
API = "/api/v1"


def database():
    with connect() as db:
        yield db


def dates(start: date = date(2024,1,1), end: date = date(2025,12,31)):
    if start > end or (end-start).days > 3660:
        raise HTTPException(422, "Select an ordered date range of at most ten years.")
    return dict(start=start, end=end)


Db = Annotated[object, Depends(database)]
Dates = Annotated[dict, Depends(dates)]


@app.get("/health")
def health(db: Db):
    db.execute("SELECT 1")
    return {"status": "ok"}


def register(key):
    def read(db: Db, params: Dates, limit: int = Query(500, ge=1, le=1000), offset: int = Query(0, ge=0)):
        return db.execute(QUERIES[key] + " LIMIT %(limit)s OFFSET %(offset)s",
                          dict(params, limit=limit, offset=offset)).fetchall()
    app.add_api_route(f"{API}/{key}", read, methods=["GET"], name=key.replace("/", "_"))


for query in QUERIES:
    register(query)


@app.get(f"{API}/experiments")
def experiments(db: Db, params: Dates):
    rows = db.execute("""
       SELECT variant,count(*) AS n,count(*) FILTER(WHERE converted) AS x
       FROM sessions WHERE visited BETWEEN %(start)s AND %(end)s GROUP BY variant
    """, params)
    return [checkout_experiment({row["variant"]: (row["n"],row["x"]) for row in rows})]


@app.get(f"{API}/experiments/sample-size")
def estimate(baseline: float, target: float, power: float = .8):
    try:
        return {"per_arm": sample_size(baseline,target,power)}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


class RefreshRequest(BaseModel):
    scale: int = Field(default=1,ge=1,le=100)


@app.post(f"{API}/pipelines/refresh", status_code=202)
def queue_refresh(body: RefreshRequest, tasks: BackgroundTasks, admin_token: str = Header(default="")):
    token = os.getenv("DATAFLOW_ADMIN_TOKEN")
    if not token or not secrets.compare_digest(token.encode(), admin_token.encode()):
        raise HTTPException(403, "A valid Admin-Token header is required.")
    tasks.add_task(refresh, body.scale)
    return {"status": "submitted", "detail": "Only one refresh publishes at a time. Check pipeline runs."}


@app.get(f"{API}/reports/export")
def export(db: Db, params: Dates, report: str = "Revenue", format: str = "xlsx"):
    db.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
    if format == "xlsx":
        return Response(workbook(db, params),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="NovaCart_Business_Analysis.xlsx"'})
    if format == "csv" and report in SHEETS:
        columns, rows = export_rows(db, SHEETS[report], params)
        return Response(csv_data(columns, rows), media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{report}.csv"'})
    raise HTTPException(422, "Select xlsx or a supported CSV report.")


dist = Path(os.getenv("DATAFLOW_DIST", str(ROOT / "web" / "dist")))
if dist.is_dir():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(dist / "index.html")
