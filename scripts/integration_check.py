"""Run against an isolated demo database with the API process listening."""
import os
import time

import httpx

from app.db import connect
from app.pipeline import refresh

BASE = "http://127.0.0.1:8000/api/v1"
token = os.environ["DATAFLOW_ADMIN_TOKEN"]

with httpx.Client(base_url=BASE, timeout=30, trust_env=False) as client:
    assert client.post("/pipelines/refresh",json={"scale":1}).status_code == 403
    assert client.post("/pipelines/refresh",json={"scale":0},headers={"Admin-Token":token}).status_code == 422
    assert client.get("/revenue/trends",params={"start":"2025-02-01","end":"2025-01-01"}).status_code == 422
    with connect() as db:
        db.execute("SELECT pg_advisory_lock(423810)")
        assert refresh() is False
    initial = client.get("/pipelines/runs").json()[0]["id"]
    assert client.post("/pipelines/refresh",json={"scale":2},headers={"Admin-Token":token}).status_code == 202
    for _ in range(120):
        latest = client.get("/pipelines/runs").json()[0]
        if latest["id"] > initial and latest["status"] != "running":
            assert latest["status"] == "succeeded", latest
            break
        time.sleep(.1)
    else:
        raise AssertionError("Refresh did not finish")
    assert client.get("/dashboard/summary").json()[0]["orders"] == 5000
    assert len(client.get("/products/performance",params={"limit":2,"offset":5}).json()) == 2
    assert all(r["failures"]==0 for r in client.get("/quality").json())
    assert refresh(scale=1)
    assert client.get("/dashboard/summary").json()[0]["orders"] == 2500
print("PASS: admin authorization, range and scale validation, lock contention, background publication, pagination and demo reset")
