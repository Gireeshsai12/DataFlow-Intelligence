# DataFlow Intelligence

DataFlow Intelligence is a local revenue, customer analytics and business intelligence platform for NovaCart, a synthetic retailer. A repeatable Python pipeline loads PostgreSQL. FastAPI serves analytics and exports. A React and TypeScript dashboard presents the data in ten screens.

## Start the demo

Install Docker Desktop on Windows or macOS, or Docker Engine with the Compose v2 plugin on Linux. Start Docker, extract the ZIP and open a terminal in the extracted DataFlow-Intelligence folder. The first build downloads container images and dependencies. No vendor account or API key is needed to run the demo.

```sh
docker compose up --build
```

Open the [dashboard](http://localhost:8000) or the [API reference](http://localhost:8000/docs) after the app starts. Port 8000 must be free. The startup scripts run detached and wait for service health.

| Action | Windows PowerShell | macOS / Linux |
|---|---|---|
| Start | `powershell -ExecutionPolicy Bypass -File .\start-windows.ps1` | `sh ./start-unix.sh` |
| Verify | `powershell -ExecutionPolicy Bypass -File .\verify-windows.ps1` | `sh ./verify.sh` |
| Stop | `powershell -ExecutionPolicy Bypass -File .\stop-windows.ps1` | `sh ./stop-unix.sh` |

Stopping the app preserves the demo database volume. The commands and app expect a dedicated demo database. The generator publishes a new synthetic snapshot and replaces the data in its own source tables. Regenerate the original snapshot and retain run history with:

```sh
docker compose exec app python -m app.pipeline --scale 1
```

Scale 1 generates 500 customers, 100 products, 2,500 orders, 6,000 website sessions and linked lines and refunds. Most dates span January 2024 through December 2025. Scale 100 targets 50,000 customers and 250,000 orders and needs substantially more memory. Scale 2 was exercised in the integration check.

## Explore the demo

1. Compare revenue, order count and active customers on Overview. Apply a date range to recalculate the report.
2. Explore monthly growth, customer segments and retention cohorts. Marketing shows cart and purchase conversion alongside campaign attribution.
3. Review the checkout experiment's estimated difference, confidence interval and p-value. Use the sample-size endpoint in the API reference to plan an experiment.
4. Open Data Quality and Pipeline Monitoring to inspect publication results.
5. Download a workbook or a CSV from Reports & Exports. A generated set is included in reports.

## Native development

Requires Python 3.12, Node.js 24, npm and a running PostgreSQL 18 server. Create a dedicated empty database named dataflow, or set DATABASE_URL to your dedicated database. Keep the database off public interfaces. Use a Python virtual environment.

```sh
python -m pip install -r requirements-dev.txt
npm --prefix web ci
npm --prefix web run build
python -m uvicorn app.main:app --port 8000
```

Startup applies the SQL migration and loads the base dataset on a fresh database. Set DATABASE_URL if the connection differs from the development default `postgresql://dataflow:dataflow@localhost:5432/dataflow`. These defaults are for local development. The packaged Compose database has no published port.

In a second terminal:

```sh
python -m pytest -q
python scripts/smoke.py
python -m playwright install chromium
python scripts/browser_check.py
dbt build --project-dir warehouse --profiles-dir warehouse
```

dbt reads DBT_HOST, DBT_PORT, DBT_USER, DBT_PASSWORD and DBT_DATABASE when set. It targets a reachable development database. The dashboard queries PostgreSQL directly and starts independently of dbt.

## Refresh and schedule

Use `python -m app.pipeline --scale 1` from the project directory with DATABASE_URL configured, or schedule the equivalent Compose command in cron or Windows Task Scheduler. Schedule one attempt per interval. If another run holds the lock, the CLI exits with an error and leaves the published data intact. Pipeline Monitoring exposes run outcomes.

For HTTP refresh, set DATAFLOW_ADMIN_TOKEN in the application environment before launching. Send it in the Admin-Token header to `POST /api/v1/pipelines/refresh` with `{"scale":1}`. The endpoint is disabled when the token is unset. Refresh work runs in the application process and only one publisher holds the database lock at a time. HTTP acknowledgement indicates submission. Consult pipeline history for completed publications. This is a single-host demo. HTTPS, multi-tenant isolation and a durable worker queue are deployment concerns beyond this package.

## Source map

| Path | Contents |
|---|---|
| app/ | FastAPI, dataset generator, publisher, SQL read models, statistical analysis, exports |
| sql/ | PostgreSQL schema, indexes and order fact view |
| web/ | Dashboard source, TypeScript settings and npm lockfile |
| warehouse/ | dbt model and tests, optional Snowflake SQL |
| tests/ and scripts/ | Unit, HTTP, integration, browser and benchmark checks |
| reports/ | Generated Excel workbook and CSV data |
| docs/ | Architecture, formulas, skill evidence and BI setup |
| .github/workflows/ | Verification workflow definition |

See [verification](VERIFICATION_REPORT.md), [architecture and formulas](docs/architecture.md), [BI setup](docs/bi/README.md) and [skill evidence](docs/skill-evidence.md).
