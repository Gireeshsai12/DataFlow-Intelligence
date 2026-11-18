# Skill evidence

| Skill | Implemented evidence | Location | Verification and scope |
|---|---|---|---|
| Advanced SQL | Range aggregates, CTEs, subqueries, generated calendar, windows | app/metrics.py | HTTP reconciliation and cohort checks |
| pandas and NumPy | Numeric and non-finite cleaning, percentiles and sample spread | app/statistics.py | Workbook export exercised |
| Data cleaning and validation | Constraints, order/refund/date integrity gates and null-safe metrics | sql/001.sql, app/pipeline.py | Seed and SQL checks pass. No external dirty-file ingestion. |
| Excel PivotTables, XLOOKUP, Power Query | Table-ready data, formula examples, import steps | reports/, docs/bi/ | Workbook parsed. Native PivotTable generation and Excel formula recalculation unverified. |
| Power BI dashboards, modeling, DAX | Model setup, M script, DAX, report layouts | docs/bi/ | Compatible files supplied. Power BI Desktop execution unverified. |
| Tableau | Compatible snapshots, charts and calculated field instructions | docs/bi/ | CSVs parsed. Tableau workbook execution unverified. |
| Visualization | KPI cards, area and bar charts, filtering | web/src/ | React and TypeScript production build passed |
| Descriptive and inferential statistics | Percentiles, sample spread, normal approximation | app/statistics.py | Workbook smoke test and reference p-value case |
| A/B tests | Two-proportion test, lift, interval, sample sizing | app/statistics.py | Pytest and live endpoint |
| KPIs, funnels and retention | Order facts, monthly cohorts, product analysis, funnel | app/metrics.py | PostgreSQL smoke and reconciliation |
| ETL and ELT | Deterministic generation, bulk load, validation, SQL marts | app/pipeline.py, warehouse/ | Live publication and scale-2 refresh; dbt build |
| dbt | Source definition, SQL model, uniqueness and null tests | warehouse/ | One model and five passing data tests |
| Snowflake | Warehouse, stage, typed load, view and grants | warehouse/snowflake/ | Optional SQL provided. Account execution unverified. |
| Dimensional modeling | Order and item grains with customer, product and campaign dimensions | sql/001.sql, docs/architecture.md | PostgreSQL constraints and seeded referential integrity |
| Python and API engineering | Context managers, dependency injection, schemas, pagination and token authorization | app/ | HTTP integration checks |
| React and TypeScript | Hooks, typed records, components and API integration | web/src/ | TypeScript and Vite builds |
| Pytest and automated checks | Seed and statistics checks, workbook reconciliation, refresh/pagination checks | tests/, scripts/ | Local tests executed |
| Playwright | Screen navigation, date range, responsive width and export flow | scripts/browser_check.py | Passed using headless Chromium |
| Docker, Bash and PowerShell | Multi-stage build, startup, shutdown and smoke verification | Dockerfile, compose.yaml, root scripts | Shell syntax checked. Docker and PowerShell execution unverified. |
| GitHub Actions | CI workflow for unit checks, Compose and Playwright | .github/workflows/ci.yml | Workflow supplied. Hosted execution unverified. |
| Performance | 30-sample sequential HTTP benchmark | scripts/smoke.py | Local latency recorded. No sustained concurrent load test. |
| Engineering documentation | Startup, metric definitions, deployment and limits | README.md, docs/ | Included |
