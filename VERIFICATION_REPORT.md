# Verification report

## Environment and outcome

Native verification ran on Linux x86-64 with Python 3.12.14, Node.js 24.22.3, PostgreSQL 18.6, dbt Core 1.13.0-b1 with postgres adapter 1.11.0, and Playwright driving headless Chromium. The API process used an isolated Python virtual environment. The PostgreSQL server listened on local TCP. The application, analytics, browser and reporting paths passed verification through their normal entry points.

| Check | Command or test | Outcome |
|---|---|---|
| Backend dependencies | `python -m venv /tmp/dataflow-clean-venv`, then its pip with `install -r requirements.txt` | Installed successfully from a fresh environment |
| Frontend clean installation and build | `npm ci` and `npm run build` in web | TypeScript and production build passed. Vite reported a chunk-size advisory. |
| First native startup | `python -m uvicorn app.main:app --port 8000` with an empty PostgreSQL database | Applied schema and automatically seeded the base dataset |
| Unit suite | `python -m pytest -q` | 6 passed, 0 failed. One dependency deprecation warning. |
| Analytics and DQ | `python scripts/smoke.py reports` | Health, OpenAPI, 10 analytics routes, no quality failures, monthly/summary reconciliation and initial cohort retention passed |
| Dataset validation | Seed tests, live quality route and report reconciliation | 500 customers, 100 products, 16 campaigns, 2,500 orders, 6,191 lines, 167 partial refunds and 6,000 sessions |
| Excel and CSV | Smoke script parses the generated workbook and all eight CSVs | All parsed. Workbook net revenue reconciled to the API. Excel Desktop rendering and formula execution were unverified. |
| API refresh and concurrency | `python -m scripts.integration_check` | Admin authorization, date/scale rejection, advisory lock contention, background publication at 5,000 orders, pagination and return to 2,500 orders passed |
| Browser E2E | `python scripts/browser_check.py` with local headless Chromium selected | Ten screens, chart rendering, date filtering, workbook download, mobile viewport and no browser errors passed |
| Warehouse SQL | `dbt build --project-dir warehouse --profiles-dir warehouse` | One materialized view model and five data tests passed against the live database |
| HTTP benchmark | 30 sequential summary requests in the smoke script | One run measured p50 25.9 ms and p95 33.2 ms on the default snapshot. Results are environment-specific. |
| Unix commands | `sh -n` on each root shell script | Syntax passed |
| Docker Compose | Docker and Compose unavailable in the test environment | Build, container startup and container health checks unverified |
| Windows/hosted CI | PowerShell and a hosted GitHub runner unavailable | Scripts and workflow supplied, execution unverified |
| ZIP | ZIP integrity check and clean extraction manifest comparison | Archive contains source, reports, configuration, screenshot, tests, and both startup scripts |

The dashboard screenshot in docs/dashboard.png was captured during a passing Playwright run.

## Optional integrations and remaining scope

- Power BI has CSV imports, Power Query M, a date-table relationship, DAX measures and setup instructions. Tableau has compatible CSVs and documented calculated fields. Snowflake has optional DDL and loading SQL. Native Power BI and Tableau workbooks and Snowflake execution were unverified.
- The app focuses on core revenue, cohorts, RFM, funnel, product sales and checkout experimentation. The brief also specified customer geography dashboards, customer acquisition cost, predictive lifetime value, inventory turnover, product reviews, some source schema fields, Welch t-tests, experiment guardrails, weekly growth, native BI artifacts and broader benchmark coverage. These were outside the implemented scope.
- The default dataset is synthetic and application-owned. External data ingestion and quarantine, durable retry orchestration, distributed rate limiting, deployment infrastructure and sustained concurrent load tests were outside the implemented scope.
- The default and scale-2 data profiles were exercised. The maximum generator scale was unverified. Treat the Compose path as unverified until it runs on a Docker host.
